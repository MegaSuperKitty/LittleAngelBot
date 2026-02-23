# -*- coding: utf-8 -*-
"""Heartbeat scheduler for periodic proactive prompts."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

from .store import JsonStore, now_iso


_DEFAULT_SPEC = {
    "enabled": False,
    "interval_seconds": 1800,
    "user_id": "web:local",
    "session_name": "",
    "prompt": "Heartbeat check-in: summarize pending items and ask what to do next.",
    "last_run_at": "",
    "last_status": "never",
    "last_result": "",
    "updated_at": "",
}


class HeartbeatEngine:
    """Single heartbeat config with background dispatcher."""

    def __init__(self, runtime, data_path: str):
        self.runtime = runtime
        self.store = JsonStore(data_path)
        self._lock = threading.Lock()
        self._spec: Dict[str, Any] = dict(_DEFAULT_SPEC)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_fire_ts = 0.0
        self._load()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="angel-heartbeat-loop")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def get_spec(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._spec)

    def update_spec(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            for key in ["enabled", "interval_seconds", "user_id", "session_name", "prompt"]:
                if key not in patch:
                    continue
                value = patch[key]
                if key == "enabled":
                    self._spec[key] = bool(value)
                elif key == "interval_seconds":
                    self._spec[key] = max(5, int(value or 0))
                else:
                    self._spec[key] = str(value or "").strip()
            self._spec["updated_at"] = now_iso()
            self._save_locked()
            return dict(self._spec)

    def run_now(self) -> Dict[str, Any]:
        threading.Thread(target=self._run_once, daemon=True).start()
        return {"accepted": True}

    def _loop(self) -> None:
        while self._running:
            should_run = False
            with self._lock:
                enabled = bool(self._spec.get("enabled", False))
                interval = max(5, int(self._spec.get("interval_seconds", 1800) or 1800))
            if enabled and (time.time() - self._last_fire_ts >= interval):
                should_run = True
            if should_run:
                self._run_once()
            time.sleep(1.0)

    def _run_once(self) -> None:
        with self._lock:
            spec = dict(self._spec)
        self._last_fire_ts = time.time()

        status = "completed"
        result = ""
        try:
            result = self.runtime.run_background_prompt(
                user_id=spec.get("user_id") or "web:local",
                session_name=spec.get("session_name") or "",
                content=spec.get("prompt") or "",
                source="heartbeat",
            )
        except Exception as exc:
            status = "failed"
            result = f"{exc}"

        with self._lock:
            self._spec["last_run_at"] = now_iso()
            self._spec["last_status"] = status
            self._spec["last_result"] = str(result or "")[:2000]
            self._spec["updated_at"] = now_iso()
            self._save_locked()

    def _load(self) -> None:
        raw = self.store.read(dict(_DEFAULT_SPEC))
        if not isinstance(raw, dict):
            raw = dict(_DEFAULT_SPEC)
        merged = dict(_DEFAULT_SPEC)
        merged.update(raw)
        merged["interval_seconds"] = max(5, int(merged.get("interval_seconds", 1800) or 1800))
        merged["enabled"] = bool(merged.get("enabled", False))
        with self._lock:
            self._spec = merged

    def _save_locked(self) -> None:
        self.store.write(self._spec)
