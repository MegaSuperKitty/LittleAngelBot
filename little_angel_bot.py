# -*- coding: utf-8 -*-
"""LittleAngelBot: compose ReAct/ReCAP, context, session manager, and tools."""

from __future__ import annotations

from typing import Optional
import json
import os

from ReAct import ReActAgent, ReActHooks
from ReCAP import ReCAPAgent
from context import LlmSummarizer, ReActContextManager
from llm_provider import get_response
from mcp import MCPRuntime, sync_mcp_runtime
from session_manager import SessionManager
from mcp.local_tools.alarm_tool import AlarmTool
from mcp.local_tools.ask_human_tool import AskHumanManager, AskHumanTool
from mcp.local_tools.skill_tool import SkillRuntime
from mcp.local_tools.sub_agent_tool import SubAgentTool
from mcp.local_tools.thinking_tool import ThinkingTool


class LittleAngelBot:
    """Unified chatbot entry class."""

    def __init__(
        self,
        history_dir: str,
        max_rounds: int = 20,
        max_steps: int = 4,
        system_prompt: Optional[str] = None,
        agent_root: Optional[str] = None,
    ):
        self._system_handler = None
        self.project_root = os.path.dirname(__file__)
        self.agent_root = agent_root or os.path.join(self.project_root, "agent_workspace")
        os.makedirs(self.agent_root, exist_ok=True)

        self.max_steps = max_steps
        self.summarizer = LlmSummarizer()
        self.session_manager = SessionManager(history_dir, max_rounds=max_rounds)
        self.context_manager: Optional[ReActContextManager] = None
        self.ask_human_manager = AskHumanManager()

        self.skill_runtime = SkillRuntime(os.path.join(self.project_root, "skills"))
        self.skill_tool = self.skill_runtime.create_tool(register=True)
        self.mcp_runtime = MCPRuntime(self.project_root)
        self._base_system_prompt = system_prompt or self._default_system_prompt()
        self.system_prompt = self._base_system_prompt

        self._react_hooks = ReActHooks()
        self._react_hook_error_mode = "isolate"

        self.tools = self._load_tools()
        self.refresh_mcp()

    def handle_message(self, user_id: str, content: str) -> Optional[str]:
        """Process one user message and return assistant text."""
        return self.run_task(user_id, content)

    def set_react_hooks(self, hooks: ReActHooks) -> None:
        """Set bot-level ReAct hooks; applied to each run-created ReActAgent."""
        self._react_hooks = hooks

    def get_react_hooks(self) -> ReActHooks:
        """Get current bot-level ReAct hooks."""
        return self._react_hooks

    def set_react_hook_error_mode(self, mode: str) -> None:
        """Set ReAct hook error strategy for future runs."""
        self._react_hook_error_mode = mode if mode in {"isolate", "strict"} else "isolate"

    def run_task(self, user_id: str, content: str, cancel_checker=None) -> Optional[str]:
        """Run one task with optional cancel checks."""
        content = (content or "").strip()
        if not content:
            return None

        command_reply = self._handle_command(user_id, content)
        if command_reply is not None:
            return command_reply

        session_path = self.session_manager.get_or_create_session_path(user_id)
        context_manager = self._create_context_manager(session_path)
        self.context_manager = context_manager
        react_agent, recap_agent = self._create_agents_for_run(context_manager)
        cancel_recorded = False

        self._bind_tool_user_context(user_id, session_path=session_path, cancel_checker=cancel_checker)
        self._bind_thinking_context()

        context_manager.append_message({"role": "user", "content": content})

        if cancel_checker and cancel_checker():
            if not cancel_recorded:
                self._record_cancel_dialog(context_manager)
                cancel_recorded = True
            return None

        messages = context_manager.get_messages()
        use_recap = self._should_use_recap(messages)
        if use_recap:
            reply_text, _ = recap_agent.run(tools=self.tools, cancel_checker=cancel_checker)
        else:
            reply_text, _ = react_agent.run(tools=self.tools, cancel_checker=cancel_checker)

        if cancel_checker and cancel_checker():
            if not cancel_recorded:
                self._record_cancel_dialog(context_manager)
                cancel_recorded = True
            return None

        self.session_manager.maybe_rename_after_rounds(user_id, context_manager.get_context_path())
        return reply_text

    def _create_context_manager(self, session_path: str) -> ReActContextManager:
        return ReActContextManager(
            context_path=session_path,
            agent_root=self.agent_root,
            summarizer=self.summarizer,
        )

    def _create_agents_for_run(
        self,
        context_manager: ReActContextManager,
    ) -> tuple[ReActAgent, ReCAPAgent]:
        react_agent = ReActAgent(
            max_steps=self.max_steps,
            context_manager=context_manager,
            system_prompt=self.system_prompt,
            hooks=self._react_hooks,
            hook_error_mode=self._react_hook_error_mode,
        )
        recap_agent = ReCAPAgent(
            base_agent=react_agent,
            context_manager=context_manager,
        )
        recap_agent.system_prompt = self.system_prompt
        return react_agent, recap_agent

    def _record_cancel_dialog(self, context_manager: ReActContextManager) -> None:
        context_manager.append_messages(
            [
                {"role": "user", "content": "结束任务"},
                {"role": "assistant", "content": "ok"},
            ]
        )

    def _handle_command(self, user_id: str, content: str) -> Optional[str]:
        if content.startswith("/listhistory"):
            names = self.session_manager.list_sessions(user_id)
            return "历史列表为空。" if not names else "历史列表：\n" + "\n".join(names)

        if content.startswith("/history"):
            parts = content.split(maxsplit=1)
            if len(parts) < 2:
                return "用法：/history 历史名"
            target = self.session_manager.switch_session(user_id, parts[1].strip())
            if target:
                name = self.session_manager.get_display_name(target)
                return f"已切换到历史：{name}"
            return "未找到该历史名。"

        if content.startswith("/newhistory"):
            path = self.session_manager.create_new_session(user_id)
            name = self.session_manager.get_display_name(path)
            return f"已新建历史：{name}"

        return None

    def _should_use_recap(self, messages) -> bool:
        """LLM-based router: choose ReCAP for multi-stage tasks."""
        prompt = (
            "你是任务路由器。判断用户最新请求是否为复杂任务。"
            "如果完成任务预计需要2步以上的LLM调用或明显多阶段规划，输出 RECAP；"
            "否则输出 REACT。只输出 RECAP 或 REACT。"
        )
        inputs = [{"role": "system", "content": self.system_prompt}]
        inputs.extend(messages[-12:])
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
            "# LittleAngelBot System Prompt\n\n"
            "你是 LittleAngelBot，一个工具优先的助手。"
            "当任务需要事实或执行动作时，优先调用工具。\n\n"
            "关键规则：\n"
            "- 工具优先，结果可验证。\n"
            "- 工具失败后要继续调整策略，不要直接放弃。\n"
            "- 运行环境是 Windows，执行命令前先做安全判断。\n"
            "- 当用户提到某个 skill 时，先调用 skill 工具加载说明，再执行。"
        )

    def _load_tools(self):
        return []

    def refresh_skills(self):
        return self.refresh_mcp()

    def refresh_mcp(self):
        return sync_mcp_runtime(self)

    def _bind_tool_user_context(self, user_id: str, session_path: str, cancel_checker=None) -> None:
        for tool in self.tools:
            if not hasattr(tool, "set_context"):
                continue
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
            elif isinstance(tool, SubAgentTool):
                tool.set_context(
                    user_id=user_id,
                    parent_context_path=session_path,
                    on_trigger=self._handle_system_message,
                )
            else:
                try:
                    tool.set_context(user_id, self._handle_system_message)
                except TypeError:
                    tool.set_context(user_id)

    def _bind_thinking_context(self) -> None:
        if self.context_manager is None:
            return
        for tool in self.tools:
            if isinstance(tool, ThinkingTool):
                tool.set_context(self.context_manager.get_messages)
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

    def _load_config(self) -> dict:
        config_path = os.getenv("LITTLE_ANGEL_CONFIG")
        if not config_path:
            default_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
            config_path = default_path if os.path.exists(default_path) else None
        if not config_path or not os.path.exists(config_path):
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}
