# -*- coding: utf-8 -*-
"""Alarm tool for scheduling a one-shot system callback at an absolute time."""

from __future__ import annotations

from datetime import datetime
import threading
from typing import Callable, Dict, Optional

from mcp.openai_tool import Tool


class AlarmTool(Tool):
    """Schedule alarm callbacks that re-enter the bot through system messages.
    
    Attributes:
        _on_trigger (Optional[Callable[[str, str], None]]): Instance field for on trigger.
        _active_user_id (Optional[str]): Unique identifier used by the instance.
        _timers (Dict[str, threading.Timer]): Instance field for timers.
    """

    def __init__(self, on_trigger: Optional[Callable[[str, str], None]] = None):
        """Initialize tool configuration and callback bindings.
        
        Args:
            on_trigger (Optional[Callable[[str, str], None]]): Input value for on trigger.
        
        Returns:
            None: This method does not return a value.
        """
        self._on_trigger = on_trigger
        self._active_user_id: Optional[str] = None
        self._timers: Dict[str, threading.Timer] = {}
        super().__init__(
            name="alarm",
            description=(
                "Set an alarm for a fixed date/time. "
                "Input must be an absolute datetime (YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS). "
                "Include the task to perform when the alarm fires."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "datetime": {
                        "type": "string",
                        "description": "Absolute datetime in YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS.",
                    },
                    "task": {
                        "type": "string",
                        "description": "What should be executed when the alarm fires.",
                    },
                },
                "required": ["datetime", "task"],
            },
        )

    def set_context(self, user_id: str, on_trigger: Optional[Callable[[str, str], None]] = None):
        """Bind the current user and optional callback override.
        
        Args:
            user_id (str): Identifier for the user.
            on_trigger (Optional[Callable[[str, str], None]]): Input value for on trigger.
        
        Returns:
            None: This method does not return a value.
        """
        self._active_user_id = user_id
        if on_trigger is not None:
            self._on_trigger = on_trigger

    def _execute(self, **kwargs):
        """Create a timer and return scheduling feedback.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        dt = _parse_datetime(kwargs.get("datetime"))
        if dt is None:
            return (
                "Invalid datetime format. "
                "Use absolute datetime: YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS."
            )

        task = (kwargs.get("task") or "").strip()
        if not task:
            return "Alarm setup failed: provide a non-empty task description."

        now = datetime_now()
        if dt <= now:
            return "Alarm time must be later than the current time."

        if not self._active_user_id or not self._on_trigger:
            return "Alarm setup failed: callback context is not bound."

        key = f"{self._active_user_id}:{dt.isoformat()}:{task}"
        delay = (dt - now).total_seconds()

        timer = threading.Timer(delay, self._fire, args=(self._active_user_id, dt, task))
        timer.daemon = True
        self._timers[key] = timer
        timer.start()

        return f"Alarm set for {dt.strftime('%Y-%m-%d %H:%M:%S')}. Task: {task}"

    def _fire(self, user_id: str, dt: datetime, task: str):
        """Emit a system message when the scheduled alarm time arrives.
        
        Args:
            user_id (str): Identifier for the user.
            dt (datetime): Input value for dt.
            task (str): Input value for task.
        
        Returns:
            None: This method does not return a value.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        content = (
            f"[system message] Alarm time reached: {dt.strftime('%Y-%m-%d %H:%M:%S')}. "
            f"Requested task: {task}"
        )
        try:
            if self._on_trigger:
                self._on_trigger(user_id, content)
        finally:
            key = f"{user_id}:{dt.isoformat()}:{task}"
            self._timers.pop(key, None)


def _parse_datetime(value: str) -> Optional[datetime]:
    """Parse supported datetime formats used by the alarm tool.
    
    Args:
        value (str): Input value for value.
    
    Returns:
        Optional[datetime]: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    text = (value or "").strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def datetime_now() -> datetime:
    """Return current local datetime (isolated for testability).
    
    Args:
        None.
    
    Returns:
        datetime: Result produced by this function.
    """
    return datetime.now()
