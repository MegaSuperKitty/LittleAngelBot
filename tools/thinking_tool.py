# -*- coding: utf-8 -*-
"""Deep reflection tool: call LLM to generate long-form analysis."""

from __future__ import annotations

from typing import Callable, List, Optional

from ReAct import get_response

from tool import Tool


class ThinkingTool(Tool):
    def __init__(self):
        self._context_provider: Optional[Callable[[], List[dict]]] = None
        super().__init__(
            name="thinking_tool",
            description=(
                "Generate a deep reflection response when the agent is stuck or needs to reassess. "
                "Use this to analyze failures, refine the plan, and decide next actions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why deep reflection is needed (e.g., repeated tool failures).",
                    }
                },
                "required": ["reason"],
            },
        )

    def set_context(self, context_provider: Optional[Callable[[], List[dict]]] = None):
        if context_provider is not None:
            self._context_provider = context_provider

    def _execute(self, **kwargs):
        reason = (kwargs.get("reason") or "").strip()
        if not reason:
            return "思考工具需要提供 reason。"

        context_text = _format_context(self._context_provider() if self._context_provider else [])

        messages = [
            {
                "role": "system",
                "content": (
                    "你是专门的思考工具。请输出不少于300字的反思内容，"
                    "分析失败原因、总结已有信息、提出替代路径，并给出明确下一步行动。"
                ),
            },
            {
                "role": "user",
                "content": f"【完整上下文】\n{context_text}\n\n【调用原因】\n{reason}",
            },
        ]

        response = get_response(messages, tools=None, stream=False)
        return (response.content or "").strip()


def _format_context(messages: List[dict]) -> str:
    if not messages:
        return "(no context)"
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = (msg.get("content") or "").strip()
        if not content:
            content = "(empty)"
        lines.append(f"{role}: {content}")
    return "\n".join(lines)
