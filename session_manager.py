# -*- coding: utf-8 -*-
"""Session routing for WeClaw.

This module manages:
- Per-user current session pointer.
- Session list/switch/new commands.
- Automatic rename after enough rounds.
- Sub-session path generation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import re
import time


def _timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())


class SessionManager:
    """Manage session file routing outside the context layer."""

    def __init__(self, base_dir: str, max_rounds: int = 100):
        self.base_dir = os.path.abspath(base_dir)
        self.max_rounds = max_rounds
        os.makedirs(self.base_dir, exist_ok=True)

    def get_or_create_session_path(self, user_id: str) -> str:
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)

        state = self._load_state(user_id)
        current_file = state.get("current_file")
        if isinstance(current_file, str) and current_file:
            current_path = os.path.join(user_dir, current_file)
            if os.path.exists(current_path):
                self._ensure_v2_session(current_path)
                return current_path

        latest = self._latest_main_session(user_dir)
        if latest:
            self._save_state(user_id, os.path.basename(latest))
            self._ensure_v2_session(latest)
            return latest

        return self.create_new_session(user_id)

    def create_new_session(self, user_id: str) -> str:
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        stem = self._unique_stem(user_dir, _timestamp())
        path = os.path.join(user_dir, f"{stem}.json")
        self._atomic_write(path, self._new_payload(name=stem))
        self._save_state(user_id, os.path.basename(path))
        return path

    def list_sessions(self, user_id: str) -> List[str]:
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return []

        items: List[str] = []
        for path in sorted(self._iter_main_session_paths(user_dir)):
            payload = self._load_payload(path)
            if not self._is_v2_payload(payload):
                continue
            items.append(str(payload.get("name") or os.path.splitext(os.path.basename(path))[0]))
        return items

    def switch_session(self, user_id: str, name: str) -> Optional[str]:
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return None
        target_name = (name or "").strip()
        if not target_name:
            return None

        for path in self._iter_main_session_paths(user_dir):
            filename = os.path.basename(path)
            stem = os.path.splitext(filename)[0]
            payload = self._load_payload(path)
            display_name = ""
            if self._is_v2_payload(payload):
                display_name = str(payload.get("name", ""))
            if target_name in {filename, stem, display_name}:
                self._save_state(user_id, filename)
                self._ensure_v2_session(path)
                return path
        return None

    def get_display_name(self, session_path: str) -> str:
        payload = self._load_payload(session_path)
        if self._is_v2_payload(payload):
            return str(payload.get("name") or os.path.splitext(os.path.basename(session_path))[0])
        return os.path.splitext(os.path.basename(session_path))[0]

    def maybe_rename_after_rounds(self, user_id: str, session_path: str) -> str:
        payload = self._load_payload(session_path)
        if not self._is_v2_payload(payload):
            payload = self._new_payload(name=os.path.splitext(os.path.basename(session_path))[0])
            self._atomic_write(session_path, payload)

        if payload.get("renamed"):
            return session_path
        rounds = int(payload.get("rounds", 0))
        if rounds < 3:
            return session_path

        first_user = ""
        for message in payload.get("messages", []):
            if message.get("role") == "user":
                first_user = str(message.get("content", ""))
                break

        created_at = str(payload.get("created_at") or _timestamp())
        slug = self._slugify(first_user) or "chat"
        new_stem = self._unique_stem(os.path.dirname(session_path), f"{created_at}_{slug}")
        new_path = os.path.join(os.path.dirname(session_path), f"{new_stem}.json")
        if os.path.abspath(new_path) == os.path.abspath(session_path):
            return session_path

        payload["name"] = new_stem
        payload["renamed"] = True
        payload["updated_at"] = _timestamp()
        self._atomic_write(new_path, payload)
        if os.path.exists(session_path):
            os.remove(session_path)
        self._save_state(user_id, os.path.basename(new_path))
        return new_path

    def build_sub_session_path(self, parent_context_path: str, suffix: Optional[str] = None) -> str:
        base, ext = os.path.splitext(parent_context_path)
        raw = suffix.strip() if isinstance(suffix, str) else _timestamp()
        safe_suffix = self._slugify(raw) or _timestamp()
        candidate = f"{base}-sub{safe_suffix}{ext or '.json'}"
        index = 1
        while os.path.exists(candidate):
            candidate = f"{base}-sub{safe_suffix}-{index}{ext or '.json'}"
            index += 1
        return candidate

    def set_current_session(self, user_id: str, session_path: str) -> None:
        self._save_state(user_id, os.path.basename(session_path))

    def _ensure_v2_session(self, path: str) -> None:
        payload = self._load_payload(path)
        if self._is_v2_payload(payload):
            return
        stem = os.path.splitext(os.path.basename(path))[0]
        self._atomic_write(path, self._new_payload(name=stem))

    def _iter_main_session_paths(self, user_dir: str):
        for fname in os.listdir(user_dir):
            if not fname.endswith(".json"):
                continue
            if fname == "state.json":
                continue
            stem = os.path.splitext(fname)[0]
            if "-sub" in stem:
                continue
            yield os.path.join(user_dir, fname)

    def _latest_main_session(self, user_dir: str) -> Optional[str]:
        candidates = list(self._iter_main_session_paths(user_dir))
        if not candidates:
            return None
        return max(candidates, key=os.path.getmtime)

    def _state_path(self, user_id: str) -> str:
        return os.path.join(self._user_dir(user_id), "state.json")

    def _load_state(self, user_id: str) -> Dict[str, Any]:
        path = self._state_path(user_id)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_state(self, user_id: str, current_file: str) -> None:
        path = self._state_path(user_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._atomic_write(path, {"current_file": current_file})

    def _load_payload(self, path: str) -> Any:
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return None

    def _is_v2_payload(self, payload: Any) -> bool:
        return isinstance(payload, dict) and int(payload.get("schema_version", 0)) == 2

    def _new_payload(self, name: str) -> Dict[str, Any]:
        now = _timestamp()
        return {
            "schema_version": 2,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "renamed": False,
            "rounds": 0,
            "messages": [],
        }

    def _atomic_write(self, path: str, payload: Dict[str, Any]) -> None:
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)

    def _slugify(self, text: str) -> str:
        clean = re.sub(r"\s+", "_", (text or "").strip())[:20]
        clean = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff-]", "", clean)
        return clean.strip("_")

    def _unique_stem(self, directory: str, stem: str) -> str:
        candidate = stem
        index = 1
        while os.path.exists(os.path.join(directory, f"{candidate}.json")):
            candidate = f"{stem}_{index}"
            index += 1
        return candidate

    def _user_dir(self, user_id: str) -> str:
        return os.path.join(self.base_dir, user_id)
