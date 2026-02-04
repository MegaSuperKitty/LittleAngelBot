# -*- coding: utf-8 -*-
"""报告结构模板工具。"""

from __future__ import annotations

from tool import Tool


class ReportTemplateTool(Tool):
    def __init__(self):
        super().__init__(
            name="report_template",
            description="Generate a structured report template with citation placeholders.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Report topic."},
                    "requirements": {"type": "string", "description": "Optional requirements."},
                },
                "required": ["topic"],
            },
        )

    def _execute(self, **kwargs):
        topic = (kwargs.get("topic") or "").strip()
        requirements = (kwargs.get("requirements") or "").strip()
        if not topic:
            return "topic 不能为空。"
        req = f"要求：{requirements}\n\n" if requirements else ""
        return (
            f"标题：{topic}\n\n"
            f"{req}"
            "1. 背景与范围\n"
            "- 背景介绍（引用来源：[#]）\n\n"
            "2. 方法与资料来源\n"
            "- 搜索关键词与来源类型\n"
            "- 资料筛选标准\n\n"
            "3. 关键发现\n"
            "- 发现 1（引用来源：[#]）\n"
            "- 发现 2（引用来源：[#]）\n\n"
            "4. 共识与分歧\n"
            "- 共识点（引用来源：[#][#]）\n"
            "- 分歧点（引用来源：[#][#]）\n\n"
            "5. 结论与建议\n"
            "- 结论\n"
            "- 建议\n\n"
            "6. 参考资料\n"
            "- [#] 标题 - URL\n"
        )
