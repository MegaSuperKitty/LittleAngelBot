# -*- coding: utf-8 -*-
"""本地时间工具。"""

from datetime import datetime

from mcp.openai_tool import Tool


class TimeTool(Tool):
    """Represent the TimeTool component.
    
    Note:
        This class currently exposes no documented instance attributes.
    """
    def __init__(self):
        """Initialize time tool state and dependencies.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        super().__init__(
            name="time",
            description="Get the current local time.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )

    def _execute(self):
        """Internal helper to execute.
        
        Args:
            None.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        now = datetime.now()
        return f"当前本地时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
