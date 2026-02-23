# -*- coding: utf-8 -*-
"""Session indexer for scanning chat history files."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SessionSummary:
    user_id: str
    channel_prefix: str
    session_name: str
    file_name: str
    file_path: str
    updated_at: str
    created_at: str
    rounds: int
    message_count: int
    is_sub_session: bool


class SessionIndexer:
    """Build metadata views over chat_history storage."""

    def __init__(self, history_dir: str):
        self.history_dir = Path(history_dir).resolve()

    def list_sessions(self) -> List[SessionSummary]:
        sessions: List[SessionSummary] = []
        if not self.history_dir.exists():
            return sessions
        for user_dir in self.history_dir.iterdir():
            if not user_dir.is_dir():
                continue
            user_id = user_dir.name
            for file_path in user_dir.glob("*.json"):
                if file_path.name == "state.json":
                    continue
                payload = self._load_json(file_path)
                session_name = self._display_name(file_path, payload)
                messages = payload.get("messages", []) if isinstance(payload, dict) else []
                sessions.append(
                    SessionSummary(
                        user_id=user_id,
                        channel_prefix=self._channel_prefix(user_id),
                        session_name=session_name,
                        file_name=file_path.name,
                        file_path=str(file_path),
                        updated_at=str((payload or {}).get("updated_at", "")),
                        created_at=str((payload or {}).get("created_at", "")),
                        rounds=int((payload or {}).get("rounds", 0) or 0),
                        message_count=len(messages) if isinstance(messages, list) else 0,
                        is_sub_session="-sub" in file_path.stem,
                    )
                )
        sessions.sort(key=lambda item: (item.updated_at or "", item.file_name), reverse=True)
        return sessions

    def get_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        path = self.find_session_path(user_id, session_name)
        if not path:
            return []
        payload = self._load_json(path)
        messages = payload.get("messages", []) if isinstance(payload, dict) else []
        return messages if isinstance(messages, list) else []

    def find_session_path(self, user_id: str, session_name: str) -> Optional[str]:
        user_dir = self.history_dir / user_id
        if not user_dir.exists() or not session_name:
            return None
        target = session_name.strip()
        for file_path in user_dir.glob("*.json"):
            if file_path.name == "state.json":
                continue
            payload = self._load_json(file_path)
            display_name = self._display_name(file_path, payload)
            if target in {file_path.name, file_path.stem, display_name}:
                return str(file_path)
        return None

    def _display_name(self, file_path: Path, payload: Any) -> str:
        if isinstance(payload, dict):
            name = payload.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        return file_path.stem

    def _channel_prefix(self, user_id: str) -> str:
        if ":" not in user_id:
            return "unknown"
        return user_id.split(":", 1)[0] or "unknown"

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}


def split_session_ref(session_ref: str) -> Tuple[str, str]:
    """Split '<user_id>::<session_name>' format."""
    text = (session_ref or "").strip()
    if "::" not in text:
        return "", ""
    user_id, session_name = text.split("::", 1)
    return user_id.strip(), session_name.strip()
