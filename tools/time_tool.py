# -*- coding: utf-8 -*-
"""本地时间工具。"""

from datetime import datetime

from tool import Tool


class TimeTool(Tool):
    def __init__(self):
        super().__init__(
            name="time",
            description="Get the current local time.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )

    def _execute(self):
        now = datetime.now()
        return f"当前本地时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
