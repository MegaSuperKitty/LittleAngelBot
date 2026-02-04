# -*- coding: utf-8 -*-
"""Tool 基类与 OpenAI tool 规范适配。"""

from typing import Any, Dict
import json


class Tool:
    """可被 OpenAI tool 调用的工具基类。"""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def spec(self) -> Dict[str, Any]:
        """返回 OpenAI tools 规范。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, arguments):
        """执行工具调用。"""
        args = self._parse_arguments(arguments)
        return self._execute(**args)

    def _execute(self, **kwargs):
        raise NotImplementedError("Tool._execute must be implemented by subclasses.")

    def _parse_arguments(self, arguments) -> Dict[str, Any]:
        if arguments is None:
            return {}
        if isinstance(arguments, dict):
            return arguments
        if isinstance(arguments, str):
            arguments = arguments.strip()
            if not arguments:
                return {}
            return json.loads(arguments)
        raise ValueError("Unsupported tool arguments type.")
