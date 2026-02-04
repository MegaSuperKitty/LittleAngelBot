# -*- coding: utf-8 -*-
"""LittleAngelBot：集成 ReAct、上下文与工具。"""

from typing import Optional
import json
import os

from ReAct import ReActAgent, get_response
from ReCAP import ReCAPAgent
from context import ContextWindowManager, HistoryManager, LlmSummarizer
from tools.bash_tool import BashTool
from tools.edit_tool import EditTool
from tools.glob_tool import GlobTool
from tools.grep_tool import GrepTool
from tools.read_tool import ReadTool
from tools.write_file_tool import WriteFileTool
from tools.cite_manager_tool import CiteManagerTool
from tools.quote_extract_tool import QuoteExtractTool
from tools.report_template_tool import ReportTemplateTool
from tools.source_compare_tool import SourceCompareTool
from tools.skill_executor_tool import SkillExecutorTool
from skill_registry import SkillRegistry
from tools.alarm_tool import AlarmTool
from tools.ask_human_tool import AskHumanManager, AskHumanTool
from tools.skill_tool import SkillTool
from tools.sub_agent_tool import SubAgentTool
from tools.time_tool import TimeTool
from tools.web_fetch_tool import WebFetchTool
from tools.zhipu_web_search_tool import ZhipuWebSearchTool
from tools.skill_init_tool import SkillInitTool
from tools.thinking_tool import ThinkingTool


class LittleAngelBot:
    """面向聊天入口的统一机器人封装。"""

    def __init__(
        self,
        history_dir: str,
        max_rounds: int = 20,
        max_steps: int = 4,
        system_prompt: Optional[str] = None,
        agent_root: Optional[str] = None,
    ):
        self._system_handler = None
        summarizer = LlmSummarizer()
        self.project_root = os.path.dirname(__file__)
        self.agent_root = agent_root or os.path.join(self.project_root, "agent_workspace")
        os.makedirs(self.agent_root, exist_ok=True)
        self.context_manager = ContextWindowManager(agent_root=self.agent_root)
        self.ask_human_manager = AskHumanManager()
        self.history_manager = HistoryManager(
            history_dir,
            max_rounds=max_rounds,
            summarizer=summarizer,
            context_manager=self.context_manager,
        )
        self.react_agent = ReActAgent(
            max_steps=max_steps,
            context_manager=self.context_manager,
            summarizer=summarizer,
        )
        self.recap_agent = ReCAPAgent(
            base_agent=self.react_agent,
            context_manager=self.context_manager,
            summarizer=summarizer,
        )
        self.skill_registry = self._load_skill_registry()
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.react_agent.system_prompt = self.system_prompt
        self.recap_agent.system_prompt = self.system_prompt
        self.tools = self._load_tools()

    def handle_message(self, user_id: str, content: str) -> Optional[str]:
        """处理用户消息，返回回复文本。"""
        return self.run_task(user_id, content)

    def run_task(self, user_id: str, content: str, cancel_checker=None) -> Optional[str]:
        """运行一次任务，可选支持取消。"""
        content = (content or "").strip()
        if not content:
            return None

        command_reply = self._handle_command(user_id, content)
        if command_reply is not None:
            return command_reply

        context = self.history_manager.open_context(user_id)
        # Bind per-user data so tools (e.g., alarm) can trigger messages back to this user.
        self._bind_tool_user_context(user_id, cancel_checker=cancel_checker)
        # Bind shared runtime context for tools that need it (e.g., thinking_tool).
        self._bind_thinking_context(context)
        context.append_message("user", content)

        messages = context.get_messages()
        if cancel_checker and cancel_checker():
            context.rollback()
            return None

        use_recap = self._should_use_recap(messages)
        if use_recap:
            reply_text, new_messages = self.recap_agent.run(
                messages, tools=self.tools, cancel_checker=cancel_checker
            )
        else:
            reply_text, new_messages = self.react_agent.run(
                messages, tools=self.tools, cancel_checker=cancel_checker
            )
        if cancel_checker and cancel_checker():
            context.rollback()
            return None

        context.append_messages(new_messages)
        context.finalize()

        return reply_text

    def _handle_command(self, user_id: str, content: str) -> Optional[str]:
        if content.startswith("/listhistory"):
            names = self.history_manager.list_histories(user_id)
            return "历史列表为空。" if not names else "历史列表：\n" + "\n".join(names)

        if content.startswith("/history"):
            parts = content.split(maxsplit=1)
            if len(parts) < 2:
                return "用法：/history 历史名"
            target = self.history_manager.switch_history(user_id, parts[1].strip())
            if target:
                name = self.history_manager.get_display_name(target)
                return f"已切换到历史：{name}"
            return "未找到该历史名。"

        if content.startswith("/newhistory"):
            path = self.history_manager.create_new_history(user_id)
            name = self.history_manager.get_display_name(path)
            return f"已新建历史：{name}"

        return None

    def _should_use_recap(self, messages) -> bool:
        """LLM-based router: use ReCAP for complex tasks, otherwise ReAct."""
        prompt = (
            "你是任务路由器。判断用户最新请求是否为复杂任务："
            "如果完成任务预计需要5步以上的LLM调用或明显多阶段计划，输出 RECAP；"
            "否则输出 REACT。只输出 RECAP 或 REACT。"
        )
        inputs = [{"role": "system", "content": self.system_prompt}]
        inputs.extend(messages[-12:])  # keep it small
        inputs.append({"role": "user", "content": prompt})
        try:
            resp = get_response(inputs, tools=None, stream=False)
            text = (resp.content or "").strip().upper()
            if "RECAP" in text:
                return True
        except Exception:
            pass
        return False

    def _default_system_prompt(self) -> str:
        return (
            """# LittleAngelBot System Prompt

你是 LittleAngelBot，一个以**工具优先**的助手。目标是可靠、可执行、可验证地完成任务。

## 核心原则

- **工具优先**：能用工具就用工具获取信息或执行操作。
- **失败不放弃**：工具调用失败并不可怕，必须从失败返回中反思原因，调整方案后继续执行。
- **安全优先**：运行环境是 Windows，执行命令前先确认安全。

## Skills 使用规则

- 当用户提到某个技能或技能相关任务时，**必须先调用 `skill` 工具加载该技能**，再按技能说明执行。
- 技能是提示词，不是可执行工具。
- 如果 `skills` 中已有**相似功能或描述**的技能，**在调用任何工具之前**必须先加载对应 skill 并阅读其 `SKILL.md`，获取说明、规范和经验，然后再按技能说明操作。
- `skills` 位于 `./skills`，具体技能在 `./skills/<skill_name>`。
- 要运行技能目录下的脚本或读取其文件，先切换到对应技能目录（或在 bash 中使用 `workdir` 指定目录），再用相对路径调用脚本（例如：在 `skills\\pptx` 下运行 `scripts\\html2pptx.js`）。执行完毕后切回工作目录。

## 系统消息说明

以 `【system commands】` 开头的是执行系统发来的消息，属于系统级提示，不是用户输入内容。

## 资料搜集与报告生成流程

1. 先用 `web_search` 查找来源
2. 用 `web_fetch` 抓取正文
3. 用 `quote_extract` 提取可引用片段
4. 用 `source_compare` 做多来源一致性与分歧分析
5. 用 `report_template` 生成报告结构
6. 用 `cite_manager` 输出参考资料清单
"""
            + self._skills_summary()
        )

    def _skills_summary(self) -> str:
        skills = self.skill_registry.list_skills()
        if not skills:
            return "\n\n[Skills]\n(No skills available.)"
        lines = ["\n\n[Skills]"]
        for meta in skills:
            if meta.description:
                lines.append(f"- {meta.name}: {meta.description}")
            elif meta.when_to_use:
                lines.append(f"- {meta.name}: {meta.when_to_use}")
            else:
                lines.append(f"- {meta.name}")
        return "\n".join(lines)

    def _load_tools(self):
        config = self._load_config()
        env_tools = os.getenv("LITTLE_ANGEL_TOOLS")
        if env_tools is not None:
            tool_names = [t.strip() for t in env_tools.split(",") if t.strip()]
        else:
            tool_names = config.get("tools", []) if config else ["bash"]

        if tool_names and len(tool_names) == 1 and tool_names[0].lower() in {"none", "off", "disable"}:
            tool_names = []

        tools = []
        for name in tool_names:
            pass
            # if name == "bash":
            #     tools.append(BashTool())
        tools.append(BashTool(self.agent_root))
        tools.append(ReadTool(self.agent_root))
        tools.append(WriteFileTool(self.agent_root))
        tools.append(GlobTool(self.agent_root))
        tools.append(GrepTool(self.agent_root))
        tools.append(EditTool(self.agent_root))
        tools.append(SkillExecutorTool(os.path.join(self.project_root, "skills")))
        tools.append(SkillInitTool(os.path.join(self.project_root, "skills")))
        tools.append(ZhipuWebSearchTool())
        tools.append(WebFetchTool())
        tools.append(QuoteExtractTool())
        tools.append(SourceCompareTool())
        tools.append(ReportTemplateTool())
        tools.append(CiteManagerTool())
        tools.append(TimeTool())
        tools.append(AlarmTool(self._handle_system_message))
        tools.append(AskHumanTool(self.ask_human_manager))
        tools.append(SkillTool(self.skill_registry))
        tools.append(SubAgentTool(tools, self.skill_registry))
        tools.append(ThinkingTool())
        return tools

    def _bind_tool_user_context(self, user_id: str, cancel_checker=None) -> None:
        for tool in self.tools:
            if hasattr(tool, "set_context"):
                if isinstance(tool, ThinkingTool):
                    continue
                if isinstance(tool, AlarmTool):
                    tool.set_context(user_id, self._handle_system_message)
                elif isinstance(tool, AskHumanTool):
                    tool.set_context(
                        user_id,
                        on_ask=self._handle_ask_human,
                        cancel_checker=cancel_checker,
                    )
                else:
                    try:
                        tool.set_context(user_id, self._handle_system_message)
                    except TypeError:
                        tool.set_context(user_id)

    def _bind_thinking_context(self, context) -> None:
        for tool in self.tools:
            if isinstance(tool, ThinkingTool):
                tool.set_context(lambda ctx=context: ctx.get_messages())
                break

    def _handle_system_message(self, user_id: str, content: str) -> Optional[str]:
        handler = self._system_handler
        if handler:
            return handler(user_id, content)
        return self.handle_message(user_id, content)

    def set_system_handler(self, handler) -> None:
        self._system_handler = handler

    def _handle_ask_human(self, user_id: str, question: str) -> None:
        handler = getattr(self, "_ask_handlers", {}).get(user_id)
        if handler:
            handler(user_id, question)

    def set_ask_handler(self, user_id: str, handler) -> None:
        if not hasattr(self, "_ask_handlers"):
            self._ask_handlers = {}
        self._ask_handlers[user_id] = handler


    def clear_ask_handler(self, user_id: str) -> None:
        if hasattr(self, "_ask_handlers"):
            self._ask_handlers.pop(user_id, None)

    def has_pending_human(self, user_id: str) -> bool:
        return self.ask_human_manager.has_pending(user_id)

    def provide_human_input(self, user_id: str, content: str) -> bool:
        return self.ask_human_manager.provide(user_id, content)

    def cancel_pending_human(self, user_id: str) -> None:
        self.ask_human_manager.cancel(user_id)

    def _load_skill_registry(self) -> SkillRegistry:
        base_dir = os.path.dirname(__file__)
        skills_dir = os.path.join(base_dir, "skills")
        registry = SkillRegistry(skills_dir)
        registry.refresh()
        return registry

    def _load_config(self) -> dict:
        config_path = os.getenv("LITTLE_ANGEL_CONFIG")
        if not config_path:
            default_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
            config_path = default_path if os.path.exists(default_path) else None
        if not config_path or not os.path.exists(config_path):
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

