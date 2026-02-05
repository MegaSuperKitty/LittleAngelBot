# -*- coding: utf-8 -*-
"""ReAct 代理与工具调用循环。"""

from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from openai import OpenAI
from context import ContextWindowManager


def get_response(prompts, tools=None, key_word="", stream=False, on_token=None):
    """调用 Qwen（DashScope 兼容）聊天模型。"""
    # 当前实现不启用流式，保留 stream 形参以兼容调用方。
    stream = False
    client = _build_client()
    payload = _build_payload(prompts, tools, key_word, stream)
    response = client.chat.completions.create(**payload)
    if not stream:
        return response.choices[0].message


def _build_client() -> OpenAI:
    api_key = os.getenv("DASHSCOPE_API_KEY", "")
    return OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def _build_payload(uml_prompts, tools, key_word: str, stream: bool) -> Dict:
    payload = {
        "model": "qwen3-max",
        "messages": uml_prompts,
        "stream": stream,
        "temperature": 0.0,
        "top_p": 0.1,
        "tools": tools or [],
        "tool_choice": "auto",
    }
    if key_word:
        payload["stop"] = key_word
    return payload


class ReActAgent:
    """最小可用的工具调用循环。"""

    def __init__(
        self,
        max_steps: int = 20,
        context_manager: Optional[ContextWindowManager] = None,
        max_context_tokens: int = 60000,
        min_keep_messages: int = 6,
        summarizer=None,
    ):
        """初始化 ReAct 代理。

        Args:
            max_steps: 迭代上限。
        """
        self.max_steps = max_steps
        self.context_manager = context_manager or ContextWindowManager(
            max_tokens=max_context_tokens,
            min_keep=min_keep_messages,
        )
        self.summarizer = summarizer
        self.system_prompt = (
            "你是一个能调用工具的助手。"
            "如有必要请优先调用工具获取信息，然后给出简洁明确的回复。"
        )

    def run(self, history: List[Dict[str, str]], tools=None, cancel_checker=None):
        """基于对话历史运行工具调用循环并返回最终回答与新增消息。"""
        tool_specs, tool_map = self._normalize_tools(tools)
        context = history if hasattr(history, "get_messages") else None
        history_messages = context.get_history_messages() if context else history
        messages = [{"role": "system", "content": self.system_prompt}] + (history_messages or [])
        if context:
            context.set_runtime_messages(messages)
        new_messages: List[Dict[str, str]] = []
        step_count = 0
        tool_call_count = 0
        tool_events: List[Dict[str, str]] = []

        for _ in range(self.max_steps):
            step_count += 1
            if cancel_checker and cancel_checker():
                return "", []
            triggered_by_non_assistant = messages and messages[-1].get("role") != "assistant"
            messages = self.context_manager.compress_messages(
                messages,
                summarizer=self.summarizer,
                preserve_system=True,
                triggered_by_non_assistant=triggered_by_non_assistant,
            )
            if context:
                context.set_runtime_messages(messages)
            message = get_response(messages, tools=tool_specs, stream=False)
            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:
                assistant_msg = self._assistant_message_with_tool_calls(message)
                messages.append(assistant_msg)
                new_messages.append(assistant_msg)
                tool_results = self._run_tool_calls_parallel(tool_calls, tool_map)
                for call, tool_result in zip(tool_calls, tool_results):
                    if cancel_checker and cancel_checker():
                        return "", []
                    tool_name = call.function.name
                    if tool_name != "skill":
                        tool_result = self.context_manager.normalize_tool_output(tool_result)
                    tool_call_count += 1
                    tool_events.append(self._summarize_tool_event(tool_name, tool_result))
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": tool_name,
                        "content": tool_result,
                    }
                    messages.append(tool_msg)
                    new_messages.append(tool_msg)
                continue

            final_text = (message.content or "").strip()
            assistant_msg = {"role": "assistant", "content": final_text}
            messages.append(assistant_msg)
            new_messages.append(assistant_msg)
            return final_text, new_messages

        final_text = self._build_max_steps_reply(
            step_count=step_count,
            tool_call_count=tool_call_count,
            tool_events=tool_events,
        )
        assistant_msg = {"role": "assistant", "content": final_text}
        new_messages.append(assistant_msg)
        return final_text, new_messages

    def _normalize_tools(self, tools) -> Tuple[List[Dict], Dict[str, object]]:
        """把 Tool 实例转换为 OpenAI tools，并构建可执行映射。"""
        tool_specs: List[Dict] = []
        tool_map: Dict[str, object] = {}
        for tool in tools or []:
            if hasattr(tool, "spec") and hasattr(tool, "name"):
                tool_specs.append(tool.spec())
                tool_map[tool.name] = tool
            elif isinstance(tool, dict):
                tool_specs.append(tool)
        return tool_specs, tool_map

    def _assistant_message_with_tool_calls(self, message) -> Dict:
        """把 SDK 的 message 转成 messages 格式。"""
        tool_calls = []
        for call in message.tool_calls:
            tool_calls.append(
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
            )
        return {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": tool_calls,
        }

    def _run_tool_call(self, call, tool_map: Dict[str, object]) -> str:
        """执行单个工具调用。"""
        name = call.function.name
        arguments = call.function.arguments
        tool = tool_map.get(name)
        if not tool:
            return f"Tool not found: {name}"
        try:
            return tool.run(arguments)
        except Exception as exc:
            return f"Tool error: {exc}"

    def _run_tool_calls_parallel(self, tool_calls, tool_map: Dict[str, object]) -> List[str]:
        """并行执行工具调用，保持输入顺序返回结果。"""
        if not tool_calls:
            return []
        max_workers = min(8, len(tool_calls))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._run_tool_call, call, tool_map) for call in tool_calls]
            return [future.result() for future in futures]

    def _summarize_tool_event(self, tool_name: str, tool_result: str) -> Dict[str, str]:
        text = tool_result if isinstance(tool_result, str) else str(tool_result)
        snippet = text[:200].replace("\n", " ").strip()
        long_path = self._extract_long_output_path(text)
        error_flag = False
        if text:
            lowered = text.lower()
            if lowered.startswith("tool error") or "error" in lowered or "错误" in text:
                error_flag = True
        return {
            "tool": tool_name,
            "snippet": snippet,
            "long_path": long_path or "",
            "error": "1" if error_flag else "0",
        }

    def _extract_long_output_path(self, text: str) -> str:
        marker = "超长被放到了（"
        if marker not in text:
            return ""
        start = text.find(marker) + len(marker)
        end = text.find("）", start)
        if end == -1:
            end = text.find(")", start)
        if end == -1:
            return ""
        return text[start:end].strip()

    def _build_max_steps_reply(self, step_count: int, tool_call_count: int, tool_events: List[Dict[str, str]]) -> str:
        summary = self._build_progress_summary(tool_events, max_tokens=200)
        lines = [
            f"已达到最大 {self.max_steps} 步执行（max_steps={self.max_steps}）。",
            f"本次已执行 {step_count} 步 / 工具调用 {tool_call_count} 次。",
            "",
            "过程摘要（≤200 tokens）：",
            summary,
            "",
            "未完成：",
            "- 尚未完成最终汇总与输出。",
            "",
            "需要你帮助：",
            "- 请补充关键缺失信息或确认是否继续执行（回复“继续”也可以）。",
        ]
        return "\n".join(lines)

    def _build_progress_summary(self, tool_events: List[Dict[str, str]], max_tokens: int = 200) -> str:
        if not tool_events:
            return "已尝试分析任务，但未执行任何工具调用，当前停在规划阶段。"

        tools = []
        long_paths = []
        errors = []
        for event in tool_events:
            name = event.get("tool", "")
            if name and name not in tools:
                tools.append(name)
            path = event.get("long_path") or ""
            if path:
                long_paths.append(path)
            if event.get("error") == "1" and name:
                errors.append(name)

        actions = []
        tool_set = set(t.lower() for t in tools)
        if any("search" in t for t in tool_set):
            actions.append("检索资料")
        if any("fetch" in t for t in tool_set):
            actions.append("抓取网页")
        if any(t == "read" or "read" in t for t in tool_set):
            actions.append("读取文件")
        if any("write" in t or "edit" in t for t in tool_set):
            actions.append("写入/编辑内容")
        if any("skill" == t or "skill" in t for t in tool_set):
            actions.append("加载技能提示")

        tools_str = "、".join(tools[:4]) + (" 等" if len(tools) > 4 else "")
        action_str = "、".join(actions) if actions else "处理中间步骤"
        parts = [
            f"已完成{action_str}（涉及 {tools_str}），并对结果做了初步处理。"
        ]

        if long_paths:
            path = long_paths[0]
            if len(long_paths) == 1:
                parts.append(f"其中有 1 次输出过长已落盘到 {path}。")
            else:
                parts.append(f"其中有 {len(long_paths)} 次输出过长，已落盘到 {path} 等。")
        if errors:
            err_tools = "、".join(sorted(set(errors))[:3]) + (" 等" if len(set(errors)) > 3 else "")
            parts.append(f"过程中出现工具报错：{err_tools}。")
        summary = " ".join(parts)
        return self._limit_text_tokens(summary, max_tokens=max_tokens)

    def _limit_text_tokens(self, text: str, max_tokens: int = 200) -> str:
        if self._estimate_text_tokens(text) <= max_tokens:
            return text
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._estimate_text_tokens(text[:mid]) <= max_tokens:
                lo = mid + 1
            else:
                hi = mid
        cut = max(0, lo - 1)
        trimmed = text[:cut].rstrip()
        if trimmed and trimmed[-1] not in "。.!?":
            trimmed += "..."
        return trimmed

    def _estimate_text_tokens(self, text: str) -> int:
        ascii_count = sum(1 for ch in text if ord(ch) < 128)
        non_ascii = len(text) - ascii_count
        return non_ascii + math.ceil(ascii_count / 4)
