# -*- coding: utf-8 -*-
"""Runtime adapter for LittleAngelBot with SSE-friendly event streaming."""

from __future__ import annotations

import asyncio
import base64
from dataclasses import asdict
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional
import uuid

from little_angel_bot import LittleAngelBot

from .file_ingest import FileIngestStore
from .react_trace_bridge import build_react_hooks
from .session_indexer import SessionIndexer
from .stream_bus import EventStreamBus


class BotRuntime:
    """Single runtime coordinating bot execution, traces, and SSE queues."""

    def __init__(
        self,
        history_dir: str,
        agent_root: str,
        max_rounds: int = 20,
        max_steps: int = 20,
        web_user_id: str = "web:local",
    ):
        self.history_dir = str(Path(history_dir).resolve())
        self.agent_root = str(Path(agent_root).resolve())
        self.web_user_id = web_user_id

        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.agent_root, exist_ok=True)

        self.bot = LittleAngelBot(
            history_dir=self.history_dir,
            max_rounds=max_rounds,
            max_steps=max_steps,
            agent_root=self.agent_root,
        )
        self.indexer = SessionIndexer(self.history_dir)
        self.files = FileIngestStore()
        self.bus = EventStreamBus()

        self._lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._cancel_flags: Dict[str, threading.Event] = {}
        self._request_user: Dict[str, str] = {}

    # ---- Session view helpers ----

    def list_sessions(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for item in self.indexer.list_sessions():
            row = asdict(item)
            storage_user_id = str(row.get("user_id", ""))
            external_user_id = self._to_external_user_id(storage_user_id)
            row["storage_user_id"] = storage_user_id
            row["user_id"] = external_user_id
            row["channel_prefix"] = self._detect_channel_prefix(external_user_id)
            rows.append(row)
        return rows

    def create_web_session(self) -> Dict[str, Any]:
        storage_user_id = self._to_storage_user_id(self.web_user_id)
        path = self.bot.session_manager.create_new_session(storage_user_id)
        name = self.bot.session_manager.get_display_name(path)
        return {
            "user_id": self.web_user_id,
            "storage_user_id": storage_user_id,
            "session_name": name,
            "path": path,
        }

    def select_session(self, user_id: str, session_name: str) -> Dict[str, Any]:
        external_uid = (user_id or "").strip() or self.web_user_id
        storage_uid = self._to_storage_user_id(external_uid)
        target = self.bot.session_manager.switch_session(storage_uid, session_name)
        if not target:
            return {"success": False, "message": "session not found"}
        return {
            "success": True,
            "user_id": external_uid,
            "storage_user_id": storage_uid,
            "session_name": self.bot.session_manager.get_display_name(target),
            "path": target,
        }

    def get_session_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        external_uid = (user_id or "").strip() or self.web_user_id
        storage_uid = self._to_storage_user_id(external_uid)
        return self.indexer.get_messages(storage_uid, session_name)

    def get_session_render_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        raw = self.get_session_messages(user_id, session_name)
        return self._normalize_messages_for_console(raw)

    # ---- File ingestion ----

    def register_uploaded_file(self, user_id: str, path: str, name: str, size: int) -> Dict[str, Any]:
        external_uid = (user_id or "").strip() or self.web_user_id
        storage_uid = self._to_storage_user_id(external_uid)
        item = self.files.add_file(storage_uid, path=path, name=name, size=size)
        return {
            "user_id": external_uid,
            "storage_user_id": storage_uid,
            "path": item.path,
            "name": item.name,
            "size": item.size,
            "ts": item.ts,
        }

    # ---- Chat stream lifecycle ----

    def start_chat_stream(self, req: Any, loop: asyncio.AbstractEventLoop):
        request_id = (getattr(req, "request_id", "") or "").strip() or str(uuid.uuid4())
        queue = self.bus.create_stream(request_id, loop)
        cancel_event = threading.Event()

        with self._lock:
            self._cancel_flags[request_id] = cancel_event
            self._request_user[request_id] = self._normalize_user_id(getattr(req, "user_id", ""))

        t = threading.Thread(
            target=self._run_chat_task,
            args=(request_id, req, cancel_event),
            daemon=True,
            name=f"angel-chat-{request_id[:8]}",
        )
        t.start()
        return request_id, queue

    def cancel_request(self, request_id: str) -> bool:
        rid = (request_id or "").strip()
        with self._lock:
            flag = self._cancel_flags.get(rid)
            user_id = self._request_user.get(rid)
        if not flag:
            return False
        flag.set()
        if user_id:
            self.bot.cancel_pending_human(user_id)
        self.bus.emit(rid, "status", {"state": "cancel_requested"})
        return True

    def provide_human_input(self, user_id: str, content: str) -> bool:
        uid = self._normalize_user_id(user_id)
        ok = self.bot.provide_human_input(uid, content)
        if ok:
            # Notify all active streams for the same user.
            with self._lock:
                targets = [rid for rid, r_uid in self._request_user.items() if r_uid == uid]
            for rid in targets:
                self.bus.emit(rid, "status", {"state": "running", "phase": "human_input_received"})
        return ok

    def cleanup_request(self, request_id: str) -> None:
        rid = (request_id or "").strip()
        with self._lock:
            self._cancel_flags.pop(rid, None)
            self._request_user.pop(rid, None)

    def run_background_prompt(self, user_id: str, session_name: str, content: str, source: str = "system") -> str:
        uid = self._normalize_user_id(user_id)
        text = str(content or "").strip()
        if not text:
            return ""

        if session_name:
            self.bot.session_manager.switch_session(uid, session_name)

        with self._run_lock:
            reply = self.bot.run_task(uid, text, cancel_checker=lambda: False)
        return str(reply or "")

    # ---- Internal helpers ----

    def _run_chat_task(self, request_id: str, req: Any, cancel_event: threading.Event) -> None:
        external_user_id = (getattr(req, "user_id", "") or "").strip() or self.web_user_id
        user_id = self._normalize_user_id(external_user_id)
        session_name = str(getattr(req, "session_name", "") or "").strip()
        content = str(getattr(req, "content", "") or "").strip()
        source = str(getattr(req, "source", "web") or "web")
        inject_uploaded_files = bool(getattr(req, "inject_uploaded_files", True))

        if not content:
            self.bus.emit(request_id, "status", {"state": "failed", "reason": "empty_content"})
            self.bus.emit(request_id, "run_done", {"success": False, "error": "empty_content"})
            self.bus.close_stream(request_id)
            self.cleanup_request(request_id)
            return

        if session_name:
            self.bot.session_manager.switch_session(user_id, session_name)

        try:
            session_path = self.bot.session_manager.get_or_create_session_path(user_id)
            session_name = self.bot.session_manager.get_display_name(session_path)
        except Exception:
            session_name = session_name or ""

        channel_prefix = self._detect_channel_prefix(external_user_id)

        self.bus.emit(
            request_id,
            "run_started",
            {
                "request_id": request_id,
                "user_id": external_user_id,
                "storage_user_id": user_id,
                "session_name": session_name,
                "channel_prefix": channel_prefix,
                "source": source,
            },
        )
        self.bus.emit(request_id, "status", {"state": "running", "phase": "boot"})

        if inject_uploaded_files:
            hint = self.files.build_prompt_hint(user_id)
            if hint:
                content = f"{hint}\n\n{content}"

        def _emit(event_type: str, payload: Dict[str, Any]) -> None:
            self.bus.emit(request_id, event_type, payload)

        hooks = build_react_hooks(_emit)
        original_hooks = self.bot.get_react_hooks()

        def ask_handler(uid: str, question: str) -> None:
            self.bus.emit(
                request_id,
                "ask_human",
                {
                    "user_id": self._to_external_user_id(uid),
                    "storage_user_id": uid,
                    "question": question,
                },
            )
            self.bus.emit(request_id, "status", {"state": "waiting", "phase": "ask_human"})

        self.bot.set_ask_handler(user_id, ask_handler)
        self.bot.set_react_hooks(hooks)

        reply_text = ""
        failed = False
        error_message = ""

        def _cancel_checker() -> bool:
            return cancel_event.is_set()

        try:
            with self._run_lock:
                reply = self.bot.run_task(user_id, content, cancel_checker=_cancel_checker)
            reply_text = str(reply or "")
            if cancel_event.is_set() and not reply_text:
                self.bus.emit(request_id, "status", {"state": "cancelled", "phase": "stopped"})
            else:
                self.bus.emit(request_id, "status", {"state": "running", "phase": "streaming_reply"})
                for chunk in self._split_chunks(reply_text, size=120):
                    self.bus.emit(request_id, "assistant_delta", {"delta": chunk})
                    time.sleep(0.005)
                self.bus.emit(request_id, "status", {"state": "completed", "phase": "done"})
        except Exception as exc:
            failed = True
            error_message = str(exc)
            self.bus.emit(request_id, "status", {"state": "failed", "phase": "error", "error": error_message})
        finally:
            self.bot.clear_ask_handler(user_id)
            self.bot.set_react_hooks(original_hooks)

            if failed:
                self.bus.emit(
                    request_id,
                    "run_done",
                    {
                        "success": False,
                        "error": error_message,
                        "request_id": request_id,
                    },
                )
            else:
                self.bus.emit(
                    request_id,
                    "run_done",
                    {
                        "success": True,
                        "request_id": request_id,
                        "user_id": external_user_id,
                        "storage_user_id": user_id,
                        "session_name": session_name,
                        "final_text": reply_text,
                    },
                )

            self.bus.close_stream(request_id)
            self.cleanup_request(request_id)

    def _normalize_user_id(self, user_id: str) -> str:
        uid = (user_id or "").strip()
        if not uid:
            uid = self.web_user_id
        return self._to_storage_user_id(uid)

    def to_storage_user_id(self, user_id: str) -> str:
        return self._to_storage_user_id(user_id)

    def to_external_user_id(self, storage_user_id: str) -> str:
        return self._to_external_user_id(storage_user_id)

    def _split_chunks(self, text: str, size: int = 120):
        if not text:
            return []
        chunks = []
        idx = 0
        while idx < len(text):
            chunks.append(text[idx : idx + size])
            idx += size
        return chunks

    def _to_storage_user_id(self, user_id: str) -> str:
        raw = (user_id or "").strip()
        if not raw:
            raw = self.web_user_id
        if raw.startswith("u_"):
            decoded = self._decode_storage_user(raw)
            if decoded is not None:
                return raw
        # Keep compatibility with old plain user dirs if value is already safe.
        invalid_chars = set('<>:"/\\|?*')
        if not any(ch in invalid_chars for ch in raw):
            return raw
        encoded = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")
        return f"u_{encoded}"

    def _to_external_user_id(self, storage_user_id: str) -> str:
        text = (storage_user_id or "").strip()
        if not text:
            return self.web_user_id
        decoded = self._decode_storage_user(text)
        if decoded is not None:
            return decoded
        return text

    def _decode_storage_user(self, storage_user_id: str) -> Optional[str]:
        text = (storage_user_id or "").strip()
        if not text.startswith("u_"):
            return None
        token = text[2:]
        if not token:
            return None
        pad_len = (4 - (len(token) % 4)) % 4
        token += "=" * pad_len
        try:
            decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
            return decoded
        except Exception:
            return None

    def _detect_channel_prefix(self, user_id: str) -> str:
        text = (user_id or "").strip()
        if ":" in text:
            return text.split(":", 1)[0] or "unknown"
        if text == "debug_user":
            return "cli"
        return "unknown"

    def _normalize_messages_for_console(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = messages if isinstance(messages, list) else []
        normalized: List[Dict[str, Any]] = []
        pending_by_call_id: Dict[str, Dict[str, Any]] = {}

        for msg in rows:
            if not isinstance(msg, dict):
                continue

            role = str(msg.get("role", "")).strip().lower()
            if role == "assistant":
                content = str(msg.get("content", "") or "")
                calls = self._parse_tool_calls(msg.get("tool_calls") or msg.get("toolCalls") or msg.get("toolcalls"))
                if calls:
                    reason = self._extract_assistant_reason(msg).strip()
                    if reason:
                        normalized.append(
                            {
                                "role": "system",
                                "kind": "thinking_card",
                                "content": reason,
                                "streaming": False,
                            }
                        )
                elif content.strip():
                    normalized.append({"role": "assistant", "content": content, "streaming": False})

                for call in calls:
                    fn = {}
                    if isinstance(call.get("function"), dict):
                        fn = call.get("function") or {}
                    elif isinstance(call.get("func"), dict):
                        fn = call.get("func") or {}

                    tool_name = str(fn.get("name") or call.get("name") or call.get("tool_name") or "tool")
                    call_id = str(call.get("id") or call.get("tool_call_id") or call.get("toolCallId") or "")
                    input_text = self._normalize_tool_payload(fn.get("arguments") if isinstance(fn, dict) else "")

                    card = {
                        "role": "system",
                        "kind": "tool_card",
                        "tool_name": tool_name,
                        "tool_call_id": call_id,
                        "input_text": input_text,
                        "output_text": "",
                        "streaming": False,
                    }
                    normalized.append(card)
                    if call_id:
                        pending_by_call_id[call_id] = card
                continue

            is_tool_like = role == "tool" or bool(msg.get("tool_call_id") or msg.get("toolCallId"))
            if is_tool_like:
                call_id = str(msg.get("tool_call_id") or msg.get("toolCallId") or "")
                tool_name = str(msg.get("name") or msg.get("tool_name") or "tool")
                output = self._normalize_tool_payload(msg.get("content") or msg.get("result") or msg.get("output") or "")

                if call_id and call_id in pending_by_call_id:
                    pending = pending_by_call_id[call_id]
                    pending["output_text"] = output
                    if not pending.get("tool_name") or pending.get("tool_name") == "tool":
                        pending["tool_name"] = tool_name
                else:
                    normalized.append(
                        {
                            "role": "system",
                            "kind": "tool_card",
                            "tool_name": tool_name,
                            "tool_call_id": call_id,
                            "input_text": "",
                            "output_text": output,
                            "streaming": False,
                        }
                    )
                continue

            if role in {"user", "system"}:
                normalized.append({"role": role, "content": str(msg.get("content", "") or ""), "streaming": False})

        return normalized

    def _extract_assistant_reason(self, msg: Dict[str, Any]) -> str:
        for key in ("reasoning_content", "reasoning", "reason"):
            text = self._extract_reason_text(msg.get(key))
            if text:
                return text
        return self._extract_reason_text(msg.get("content"))

    def _extract_reason_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts: List[str] = []
            for item in value:
                if isinstance(item, str):
                    text = item.strip()
                    if text:
                        parts.append(text)
                    continue
                if not isinstance(item, dict):
                    continue
                item_type = str(item.get("type", "") or "").strip().lower()
                if item_type not in {"thinking", "reasoning", "reasoning_content", "text", "output_text", "input_text"}:
                    continue
                text = str(
                    item.get("thinking")
                    or item.get("reasoning")
                    or item.get("text")
                    or ""
                ).strip()
                if text:
                    parts.append(text)
            return "".join(parts).strip()
        if isinstance(value, dict):
            item_type = str(value.get("type", "") or "").strip().lower()
            if item_type in {"thinking", "reasoning", "reasoning_content", "text", "output_text", "input_text"}:
                return str(
                    value.get("thinking")
                    or value.get("reasoning")
                    or value.get("text")
                    or ""
                ).strip()
            if "text" in value:
                return str(value.get("text") or "").strip()
            return ""
        return str(value).strip()

    def _parse_tool_calls(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            return [value]
        if isinstance(value, str):
            parsed = self._safe_json_loads(value)
            if isinstance(parsed, list):
                return [row for row in parsed if isinstance(row, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        return []

    def _normalize_tool_payload(self, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""

        parsed = self._safe_json_loads(text)
        if isinstance(parsed, str):
            nested = self._safe_json_loads(parsed)
            parsed = nested if nested is not None else parsed

        if parsed is None:
            return text
        if isinstance(parsed, str):
            return parsed
        try:
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            return text

    def _safe_json_loads(self, value: str) -> Optional[Any]:
        try:
            return json.loads(value)
        except Exception:
            return None
