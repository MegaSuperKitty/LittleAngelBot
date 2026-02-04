# -*- coding: utf-8 -*-
"""闹钟工具：仅支持固定日期时间。"""

from datetime import datetime
import threading
from typing import Callable, Dict, Optional

from tool import Tool


class AlarmTool(Tool):
    def __init__(self, on_trigger: Optional[Callable[[str, str], None]] = None):
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
                        "description": "What the user wants to do when the alarm fires.",
                    },
                },
                "required": ["datetime", "task"],
            },
        )

    def set_context(self, user_id: str, on_trigger: Optional[Callable[[str, str], None]] = None):
        self._active_user_id = user_id
        if on_trigger is not None:
            self._on_trigger = on_trigger

    def _execute(self, **kwargs):
        dt = _parse_datetime(kwargs.get("datetime"))
        if dt is None:
            return "闹钟时间格式错误，请使用固定日期时间：YYYY-MM-DD HH:MM 或 YYYY-MM-DD HH:MM:SS。"
        task = (kwargs.get("task") or "").strip()
        if not task:
            return "闹钟设置失败：请提供闹钟到点后要执行的任务描述。"

        now = datetime_now()
        if dt <= now:
            return "闹钟时间必须晚于当前时间。"

        if not self._active_user_id or not self._on_trigger:
            return "闹钟设置失败：未绑定触发上下文。"

        key = f"{self._active_user_id}:{dt.isoformat()}:{task}"
        delay = (dt - now).total_seconds()
        timer = threading.Timer(delay, self._fire, args=(self._active_user_id, dt, task))
        timer.daemon = True
        self._timers[key] = timer
        timer.start()
        return f"闹钟已设置：{dt.strftime('%Y-%m-%d %H:%M:%S')}，任务：{task}"

    def _fire(self, user_id: str, dt: datetime, task: str):
        content = (
            f"【system message】闹钟时间到：{dt.strftime('%Y-%m-%d %H:%M:%S')}。"
            f"你当时的要求是：{task}"
        )
        try:
            if self._on_trigger:
                self._on_trigger(user_id, content)
        finally:
            key = f"{user_id}:{dt.isoformat()}:{task}"
            self._timers.pop(key, None)


def _parse_datetime(value: str) -> Optional[datetime]:
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
    return datetime.now()
