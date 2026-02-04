# -*- coding: utf-8 -*-
"""AskHuman tool: pause and wait for human input."""

from __future__ import annotations

from typing import Callable, Dict, Optional
import threading
import time

from tool import Tool


class AskHumanTool(Tool):
    def __init__(self, manager: "AskHumanManager"):
        self._manager = manager
        self._active_user_id: Optional[str] = None
        self._ask_handler: Optional[Callable[[str, str], None]] = None
        self._cancel_checker: Optional[Callable[[], bool]] = None
        super().__init__(
            name="ask_human",
            description=(
                "Ask the user a question and wait for the reply. "
                "Use when you must confirm or request missing info."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to ask the user."},
                },
                "required": ["question"],
            },
        )

    def set_context(
        self,
        user_id: str,
        on_ask: Optional[Callable[[str, str], None]] = None,
        cancel_checker: Optional[Callable[[], bool]] = None,
    ):
        self._active_user_id = user_id
        if on_ask is not None:
            self._ask_handler = on_ask
        if cancel_checker is not None:
            self._cancel_checker = cancel_checker

    def _execute(self, **kwargs):
        question = (kwargs.get("question") or "").strip()
        if not question:
            return "AskHuman error: question is required."
        if not self._active_user_id:
            return "AskHuman error: user context not bound."
        return self._manager.ask(
            self._active_user_id,
            question,
            on_ask=self._ask_handler,
            cancel_checker=self._cancel_checker,
        )


class AskHumanManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._pending: Dict[str, Dict[str, object]] = {}

    def has_pending(self, user_id: str) -> bool:
        with self._lock:
            return user_id in self._pending

    def ask(
        self,
        user_id: str,
        question: str,
        on_ask: Optional[Callable[[str, str], None]] = None,
        cancel_checker: Optional[Callable[[], bool]] = None,
    ) -> str:
        event = threading.Event()
        with self._lock:
            self._pending[user_id] = {
                "event": event,
                "response": None,
                "question": question,
            }
        if on_ask:
            on_ask(user_id, question)

        while True:
            if cancel_checker and cancel_checker():
                self.cancel(user_id)
                return ""
            if event.wait(timeout=0.2):
                break
        with self._lock:
            data = self._pending.pop(user_id, None)
        if not data:
            return ""
        response = data.get("response")
        return "" if response is None else str(response).strip()

    def provide(self, user_id: str, response: str) -> bool:
        with self._lock:
            data = self._pending.get(user_id)
            if not data:
                return False
            data["response"] = response
            event: threading.Event = data["event"]
            event.set()
        return True

    def cancel(self, user_id: str) -> None:
        with self._lock:
            data = self._pending.get(user_id)
            if not data:
                return
            data["response"] = ""
            event: threading.Event = data["event"]
            event.set()
