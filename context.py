# -*- coding: utf-8 -*-
"""Unified single-context storage and ReAct-specific context behavior."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import math
import os
import time

from llm_provider import get_response


def _timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())


class ContextManager:
    """Base context manager.

    This class only provides:
    - Single-file message persistence.
    - Minimal message validation.
    - Atomic write-through storage.
    """

    VALID_ROLES = {"system", "user", "assistant", "tool"}

    def __init__(
        self,
        context_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        write_through: bool = True,
    ):
        if context_path:
            path = os.path.abspath(context_path)
        else:
            base = os.path.abspath(base_dir or os.path.join(os.getcwd(), "chat_history"))
            os.makedirs(base, exist_ok=True)
            path = os.path.join(base, f"{_timestamp()}.json")

        self._context_path = path
        self._write_through = bool(write_through)
        os.makedirs(os.path.dirname(self._context_path), exist_ok=True)

        self._payload: Dict[str, Any] = self._load_or_init_payload()
        if self._write_through:
            self.save()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return a safe copy of current messages."""
        return [dict(message) for message in self._payload.get("messages", [])]

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Replace messages with validated values."""
        normalized = [self._normalize_message(message) for message in (messages or [])]
        self._payload["messages"] = normalized
        self._touch_metadata()
        if self._write_through:
            self.save()

    def append_message(self, message: Dict[str, Any]) -> None:
        """Append one validated message."""
        normalized = self._normalize_message(message)
        self._payload.setdefault("messages", []).append(normalized)
        self._touch_metadata()
        if self._write_through:
            self.save()

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Append messages one by one."""
        for message in messages or []:
            self.append_message(message)

    def reload(self) -> None:
        """Reload payload from file."""
        self._payload = self._load_or_init_payload()
        if self._write_through:
            self.save()

    def save(self) -> None:
        """Persist payload to disk using atomic replace."""
        self._touch_metadata()
        self._atomic_write(self._context_path, self._payload)

    def get_context_path(self) -> str:
        """Return bound context file path."""
        return self._context_path

    def _load_or_init_payload(self) -> Dict[str, Any]:
        filename = os.path.splitext(os.path.basename(self._context_path))[0]
        if not os.path.exists(self._context_path):
            return self._new_payload(name=filename)

        try:
            with open(self._context_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            return self._new_payload(name=filename)

        payload = self._coerce_payload(data, default_name=filename)
        return payload

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

    def _coerce_payload(self, data: Any, default_name: str) -> Dict[str, Any]:
        if not isinstance(data, dict) or int(data.get("schema_version", 0)) != 2:
            return self._new_payload(name=default_name)

        created_at = str(data.get("created_at") or _timestamp())
        normalized: Dict[str, Any] = {
            "schema_version": 2,
            "name": str(data.get("name") or default_name),
            "created_at": created_at,
            "updated_at": str(data.get("updated_at") or _timestamp()),
            "renamed": bool(data.get("renamed", False)),
            "rounds": 0,
            "messages": [],
        }
        raw_messages = data.get("messages")
        if isinstance(raw_messages, list):
            for message in raw_messages:
                try:
                    normalized["messages"].append(self._normalize_message(message))
                except ValueError:
                    continue
        normalized["rounds"] = self._count_rounds(normalized["messages"])
        return normalized

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(message, dict):
            raise ValueError("message must be dict")
        role = message.get("role")
        if role not in self.VALID_ROLES:
            raise ValueError(f"invalid role: {role}")

        normalized = dict(message)
        if "content" not in normalized or normalized.get("content") is None:
            normalized["content"] = ""
        elif not isinstance(normalized.get("content"), str):
            normalized["content"] = str(normalized.get("content"))
        return normalized

    def _touch_metadata(self) -> None:
        self._payload["updated_at"] = _timestamp()
        self._payload["rounds"] = self._count_rounds(self._payload.get("messages", []))

    def _count_rounds(self, messages: List[Dict[str, Any]]) -> int:
        user_count = sum(1 for msg in messages if msg.get("role") == "user")
        assistant_count = sum(1 for msg in messages if msg.get("role") == "assistant")
        return min(user_count, assistant_count)

    def _atomic_write(self, path: str, data: Dict[str, Any]) -> None:
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)


class ReActContextManager(ContextManager):
    """ReAct context manager with compression and tool-output normalization."""

    def __init__(
        self,
        context_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        write_through: bool = True,
        max_tokens: int = 60000,
        min_keep: int = 6,
        agent_root: Optional[str] = None,
        tool_output_dir: Optional[str] = None,
        summarizer=None,
    ):
        self.max_tokens = max_tokens
        self.min_keep = max(1, int(min_keep))
        self.agent_root = os.path.abspath(agent_root) if agent_root else None
        self.summarizer = summarizer
        if tool_output_dir:
            self.tool_output_dir = tool_output_dir
        elif self.agent_root:
            self.tool_output_dir = os.path.join(self.agent_root, "tool_outputs")
        else:
            self.tool_output_dir = None
        self._tool_output_index = 0
        super().__init__(context_path=context_path, base_dir=base_dir, write_through=write_through)
        self.set_messages(self.get_messages())

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        normalized = [self._normalize_for_react(message) for message in (messages or [])]
        compressed = self.compress_messages(normalized, preserve_system=True)
        self._payload["messages"] = compressed
        self._touch_metadata()
        if self._write_through:
            self.save()

    def append_message(self, message: Dict[str, Any]) -> None:
        normalized = self._normalize_for_react(message)
        updated = self.get_messages() + [normalized]
        compressed = self.compress_messages(updated, preserve_system=True)
        self._payload["messages"] = compressed
        self._touch_metadata()
        if self._write_through:
            self.save()

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        for message in messages or []:
            self.append_message(message)

    def _normalize_for_react(self, message: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self._normalize_message(message)
        if normalized.get("role") == "tool":
            tool_name = normalized.get("name") or normalized.get("tool_name")
            if tool_name != "skill":
                normalized["content"] = self.normalize_tool_output(normalized.get("content", ""))
        return normalized

    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        total_chars = 0
        for msg in messages:
            total_chars += len(str(msg.get("role", ""))) + 1
            content = msg.get("content", "")
            if content:
                total_chars += len(str(content))
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                total_chars += len(json.dumps(tool_calls, ensure_ascii=False))
        return math.ceil(total_chars / 4)

    def window_messages(self, messages: List[Dict[str, Any]], preserve_system: bool = True) -> List[Dict[str, Any]]:
        if not messages:
            return []
        if self.estimate_tokens(messages) <= self.max_tokens:
            return list(messages)

        start_idx = 0
        system_msg: List[Dict[str, Any]] = []
        if preserve_system and messages[0].get("role") == "system":
            start_idx = 1
            system_msg = [messages[0]]

        body = messages[start_idx:]
        if not body:
            return list(messages)

        keep = body[-self.min_keep :]
        window = system_msg + keep
        while self.estimate_tokens(window) > self.max_tokens and len(keep) > 1:
            keep = keep[1:]
            window = system_msg + keep
        return window

    def compress_messages(self, messages: List[Dict[str, Any]], preserve_system: bool = True) -> List[Dict[str, Any]]:
        if not messages:
            return []
        if messages[-1].get("role") == "assistant":
            return list(messages)
        if self.estimate_tokens(messages) < self.max_tokens:
            return list(messages)

        start_idx = 0
        system_msg: List[Dict[str, Any]] = []
        if preserve_system and messages[0].get("role") == "system":
            start_idx = 1
            system_msg = [messages[0]]

        body = messages[start_idx:]
        if len(body) <= 3:
            return list(messages)

        removed = body[:-3]
        kept = body[-3:]
        summary = self._summarize_messages(removed)
        summary_msg = {"role": "user", "content": f"[ContextSummary] {summary}"}
        return system_msg + [summary_msg] + kept

    def normalize_tool_output(self, content: Any) -> str:
        if content is None:
            return ""
        text = content if isinstance(content, str) else str(content)
        if len(text) <= 10000:
            return text
        if text.startswith("Tool output too long. Stored at:"):
            return text

        output_path = self._write_tool_output(text)
        if output_path:
            rel_path = os.path.relpath(output_path, self.agent_root) if self.agent_root else output_path
            prefix = (
                "Tool output too long. Stored at: "
                f"{rel_path}. Use read tool for the full content. Preview(1000 chars):\n"
            )
        else:
            prefix = "Tool output too long. Storage path unavailable. Preview(1000 chars):\n"
        return prefix + text[:1000]

    def _write_tool_output(self, content: str) -> Optional[str]:
        if not self.tool_output_dir:
            return None
        os.makedirs(self.tool_output_dir, exist_ok=True)
        self._tool_output_index += 1
        filename = f"tool_output_{_timestamp()}_{self._tool_output_index}.txt"
        path = os.path.join(self.tool_output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            return path
        except Exception:
            return None

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        if self.summarizer:
            try:
                summary = self.summarizer.summarize(messages)
                if summary:
                    return summary.strip()
            except Exception:
                pass
        return self._fallback_structured_summary(messages)

    def _fallback_structured_summary(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return self._format_structured_summary(
                facts=["none"],
                done=["unknown"],
                todo=["unknown"],
                constraints=["unknown"],
                next_steps=["none"],
            )

        facts: List[str] = []
        done: List[str] = []
        todo: List[str] = []
        constraints: List[str] = []

        for msg in messages:
            role = str(msg.get("role", "user"))
            content = str(msg.get("content", "")).strip().replace("\n", " ")
            if not content:
                continue
            content = content[:120] + ("..." if len(content) > 120 else "")

            if role == "user" and len(facts) < 3:
                facts.append(content)
            if role == "assistant" and len(done) < 3 and any(
                key in content.lower() for key in ["done", "completed", "fixed", "implemented", "updated"]
            ):
                done.append(content)
            if len(todo) < 3 and any(key in content.lower() for key in ["need", "todo", "next", "please"]):
                todo.append(content)
            if len(constraints) < 3 and any(
                key in content.lower() for key in ["must", "cannot", "limit", "requirement", "note"]
            ):
                constraints.append(content)

        if not facts:
            facts = ["unknown"]
        if not done:
            done = ["unknown"]
        if not todo:
            todo = ["unknown"]
        if not constraints:
            constraints = ["unknown"]

        next_steps = todo[:2] if todo else ["unknown"]
        return self._format_structured_summary(facts, done, todo, constraints, next_steps)

    def _format_structured_summary(
        self,
        facts: List[str],
        done: List[str],
        todo: List[str],
        constraints: List[str],
        next_steps: List[str],
    ) -> str:
        return (
            "Facts: " + " ; ".join(facts) + "\n"
            "Done: " + " ; ".join(done) + "\n"
            "Todo: " + " ; ".join(todo) + "\n"
            "Constraints: " + " ; ".join(constraints) + "\n"
            "Next: " + " ; ".join(next_steps)
        )


class LlmSummarizer:
    """LLM-based conversation summarizer."""

    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_chars: int = 500,
    ):
        self.model = model or os.getenv("LLM_SUMMARIZER_MODEL", "")
        self.provider = provider or os.getenv("LLM_PROVIDER", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.max_output_chars = max_output_chars

    def summarize(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return (
                "Facts: none\n"
                "Done: unknown\n"
                "Todo: unknown\n"
                "Constraints: unknown\n"
                "Next: none"
            )

        content = self._format_messages(messages, max_chars=4000)
        prompt = (
            "Summarize the conversation into concise structured Chinese lines.\n"
            "Use exactly these fields and no extra text:\n"
            "Facts: ...\n"
            "Done: ...\n"
            "Todo: ...\n"
            "Constraints: ...\n"
            "Next: ...\n"
            "Do not fabricate facts.\n"
            "Conversation:\n"
            f"{content}"
        )

        response = get_response(
            prompts=[
                {"role": "system", "content": "You are a strict conversation summarizer."},
                {"role": "user", "content": prompt},
            ],
            tools=None,
            stream=False,
            temperature=0.0,
            top_p=0.1,
            provider=self.provider or None,
            base_url=self.base_url or None,
            api_key=self.api_key or None,
            model=self.model or None,
            max_tokens=1024,
        )
        text = (response.content or "").strip()
        if self.max_output_chars and len(text) > self.max_output_chars:
            text = text[: self.max_output_chars].rstrip() + "..."
        return text

    def _format_messages(self, messages: List[Dict[str, Any]], max_chars: int = 4000) -> str:
        parts: List[str] = []
        total = 0
        for msg in messages:
            role = str(msg.get("role", "user"))
            content = str(msg.get("content", "")).strip().replace("\n", " ")
            line = f"{role}: {content}"
            parts.append(line)
            total += len(line) + 1
            if total >= max_chars:
                break
        text = "\n".join(parts)
        if total >= max_chars:
            text += "\n..."
        return text
