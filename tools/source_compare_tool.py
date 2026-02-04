# -*- coding: utf-8 -*-
"""多来源对比工具。"""

from __future__ import annotations

from typing import List

from tool import Tool


class SourceCompareTool(Tool):
    def __init__(self):
        super().__init__(
            name="source_compare",
            description="Compare multiple source summaries and output consensus and differences.",
            parameters={
                "type": "object",
                "properties": {
                    "summaries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of source summaries.",
                    },
                },
                "required": ["summaries"],
            },
        )

    def _execute(self, **kwargs):
        summaries = kwargs.get("summaries") or []
        if not summaries:
            return "没有可对比的来源摘要。"
        cleaned = [s.strip() for s in summaries if str(s).strip()]
        if not cleaned:
            return "没有可对比的来源摘要。"
        lines = [
            "【共识】",
            "- （根据多个来源的共同描述填写）",
            "",
            "【分歧】",
            "- （列出来源之间不一致或冲突的点）",
            "",
            "【不确定/需要补充】",
            "- （标注信息不足或需要进一步验证的点）",
        ]
        return "\n".join(lines)
