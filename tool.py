# -*- coding: utf-8 -*-
"""Tool 基类与 OpenAI tool 规范适配。"""

from typing import Any, Dict
import json


class Tool:
    """可被 OpenAI tool 调用的工具基类。.
    
    Attributes:
        name (str): Instance field for name.
        description (str): Instance field for description.
        parameters (Dict[str, Any]): Instance field for parameters.
    """

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        """Initialize a new Tool instance.
        
        Args:
            name (str): Input value for name.
            description (str): Input value for description.
            parameters (Dict[str, Any]): Input value for parameters.
        
        Returns:
            None: This method does not return a value.
        """
        self.name = name
        self.description = description
        self.parameters = parameters

    def spec(self) -> Dict[str, Any]:
        """返回 OpenAI tools 规范。.
        
        Args:
            None.
        
        Returns:
            Dict[str, Any]: Result produced by this function.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, arguments):
        """执行工具调用。.
        
        Args:
            arguments (Any): Input value for arguments.
        
        Returns:
            Any: Execution result produced by the operation.
        """
        args = self._parse_arguments(arguments)
        return self._execute(**args)

    def _execute(self, **kwargs):
        """Internal helper to execute.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            None: This method does not return a value.
        
        Raises:
            NotImplementedError: Raised when an execution error occurs.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        raise NotImplementedError("Tool._execute must be implemented by subclasses.")

    def _parse_arguments(self, arguments) -> Dict[str, Any]:
        """Internal helper to parse arguments.
        
        Args:
            arguments (Any): Input value for arguments.
        
        Returns:
            Dict[str, Any]: Result produced by this function.
        
        Raises:
            ValueError: Raised when an execution error occurs.
        
        Note:
            This is a private helper used internally by the module/class.
        """
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
