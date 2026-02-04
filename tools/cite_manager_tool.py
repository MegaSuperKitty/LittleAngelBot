# -*- coding: utf-8 -*-
"""引用管理工具。"""

from __future__ import annotations

from tool import Tool


class CiteManagerTool(Tool):
    def __init__(self):
        super().__init__(
            name="cite_manager",
            description="Format a list of sources into numbered references.",
            parameters={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of sources (title and/or URL).",
                    },
                },
                "required": ["sources"],
            },
        )

    def _execute(self, **kwargs):
        sources = kwargs.get("sources") or []
        cleaned = [s.strip() for s in sources if str(s).strip()]
        if not cleaned:
            return "没有可用的参考资料。"
        lines = [f"[{idx}] {src}" for idx, src in enumerate(cleaned, start=1)]
        return "\n".join(lines)
