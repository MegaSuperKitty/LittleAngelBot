# -*- coding: utf-8 -*-
"""Upload file registry for auto-injection into chat prompts."""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Dict, List


@dataclass
class UploadedFile:
    user_id: str
    path: str
    name: str
    size: int
    ts: float


class FileIngestStore:
    """Thread-safe uploaded file memory store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_user: Dict[str, List[UploadedFile]] = {}

    def add_file(self, user_id: str, path: str, name: str, size: int) -> UploadedFile:
        item = UploadedFile(
            user_id=user_id,
            path=path,
            name=name,
            size=int(size),
            ts=time.time(),
        )
        with self._lock:
            self._by_user.setdefault(user_id, []).append(item)
            # Keep recent 20 files max for prompt hints.
            self._by_user[user_id] = self._by_user[user_id][-20:]
        return item

    def list_files(self, user_id: str) -> List[UploadedFile]:
        with self._lock:
            return list(self._by_user.get(user_id, []))

    def build_prompt_hint(self, user_id: str) -> str:
        files = self.list_files(user_id)
        if not files:
            return ""
        recent = files[-5:]
        lines = ["[UploadedFiles]"]
        for item in recent:
            lines.append(f"- {item.name} ({item.path})")
        return "\n".join(lines)
