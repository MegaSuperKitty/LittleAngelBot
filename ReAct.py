# -*- coding: utf-8 -*-
"""ReAct 代理与工具调用循环。"""

from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import json
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

        for _ in range(self.max_steps):
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

        final_text = "我需要更多步骤才能完成，但已达到上限。请简化问题或重试。"
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
