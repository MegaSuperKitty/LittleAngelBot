# -*- coding: utf-8 -*-
"""提取可引用片段。"""

from __future__ import annotations

from typing import List, Optional
import re

from tool import Tool


class QuoteExtractTool(Tool):
    def __init__(self):
        super().__init__(
            name="quote_extract",
            description="Extract key quotes/snippets from a text for citation.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input text."},
                    "max_quotes": {"type": "integer", "description": "Maximum number of quotes."},
                    "max_chars": {"type": "integer", "description": "Maximum chars per quote."},
                },
                "required": ["text"],
            },
        )

    def _execute(self, **kwargs):
        text = (kwargs.get("text") or "").strip()
        if not text:
            return "没有可提取的文本。"
        max_quotes = int(kwargs.get("max_quotes") or 5)
        max_chars = int(kwargs.get("max_chars") or 220)
        sentences = _split_sentences(text)
        quotes = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if len(s) > max_chars:
                s = s[: max_chars].rstrip() + "..."
            quotes.append(s)
            if len(quotes) >= max_quotes:
                break
        if not quotes:
            return "未提取到引用片段。"
        return "\n".join(f"- {q}" for q in quotes)


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[。！？.!?])\s+", text)
    if len(parts) == 1:
        parts = text.splitlines()
    return [p.strip() for p in parts if p.strip()]
