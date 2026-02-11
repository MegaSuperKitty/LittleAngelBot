from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import math
import os
import re
import time

from llm_provider import get_response


class ContextWindowManager:
    """Handle context compression and large tool output normalization."""

    def __init__(
        self,
        max_tokens: int = 60000,
        min_keep: int = 6,
        agent_root: Optional[str] = None,
        tool_output_dir: Optional[str] = None,
    ):
        self.max_tokens = max_tokens
        self.min_keep = max(1, int(min_keep))
        self.agent_root = os.path.abspath(agent_root) if agent_root else None
        if tool_output_dir:
            self.tool_output_dir = tool_output_dir
        elif self.agent_root:
            self.tool_output_dir = os.path.join(self.agent_root, "tool_outputs")
        else:
            self.tool_output_dir = None
        self._tool_output_index = 0

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

    def compress_messages(
        self,
        messages: List[Dict[str, Any]],
        summarizer=None,
        preserve_system: bool = True,
        triggered_by_non_assistant: bool = True,
    ) -> List[Dict[str, Any]]:
        if not messages:
            return []
        if not triggered_by_non_assistant:
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
        summary = self._summarize_messages(removed, summarizer)
        summary_msg = {"role": "user", "content": f"[ContextSummary] {summary}"}
        return system_msg + [summary_msg] + kept

    def _summarize_messages(self, messages: List[Dict[str, Any]], summarizer=None) -> str:
        if summarizer:
            try:
                summary = summarizer.summarize(messages)
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
        filename = f"tool_output_{time.strftime('%Y%m%d_%H%M%S')}_{self._tool_output_index}.txt"
        path = os.path.join(self.tool_output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            return path
        except Exception:
            return None


class ConversationContext:
    """In-memory wrapper around one history file."""

    def __init__(self, history_manager: "HistoryManager", history_path: str, user_id: Optional[str] = None):
        self._history_manager = history_manager
        self.history_path = history_path
        self.user_id = user_id
        self._runtime_messages: Optional[List[Dict[str, Any]]] = None
        self._messages: List[Dict[str, Any]] = []
        self._baseline_count = 0
        self._reload()
        self._baseline_count = len(self._messages)

    def _reload(self) -> None:
        data = self._history_manager._load_history(self.history_path)
        self._messages = data.get("messages", [])

    def get_messages(self) -> List[Dict[str, Any]]:
        return self._runtime_messages if self._runtime_messages is not None else self._messages

    def get_history_messages(self) -> List[Dict[str, Any]]:
        return self._messages

    def set_runtime_messages(self, messages: List[Dict[str, Any]]) -> None:
        self._runtime_messages = messages

    def clear_runtime_messages(self) -> None:
        self._runtime_messages = None

    def append_message(self, role: str, content: str) -> None:
        self._history_manager.append_message(self.history_path, role, content)
        self._reload()
        self.clear_runtime_messages()

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        self._history_manager.append_messages(self.history_path, messages)
        self._reload()
        self.clear_runtime_messages()

    def rollback(self) -> None:
        self._history_manager.truncate_history(self.history_path, self._baseline_count)
        self._reload()
        self.clear_runtime_messages()

    def finalize(self) -> str:
        rounds = self._history_manager.get_rounds(self.history_path)
        new_path = self._history_manager.maybe_rename_after_rounds(self.history_path, rounds)
        if new_path != self.history_path:
            self.history_path = new_path
            if self.user_id:
                self._history_manager.set_current_history(self.user_id, new_path)
        return self.history_path


class HistoryManager:
    """Local history manager with per-user isolation."""

    def __init__(
        self,
        base_dir: str,
        max_rounds: int = 100,
        summarizer=None,
        context_manager: Optional[ContextWindowManager] = None,
    ):
        self.base_dir = base_dir
        self.max_rounds = max_rounds
        self.summarizer = summarizer
        self.context_manager = context_manager
        os.makedirs(self.base_dir, exist_ok=True)

    def get_or_create_history(self, user_id: str) -> str:
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        state_path = os.path.join(user_dir, "state.json")

        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as handle:
                state = json.load(handle)
            current = state.get("current_file")
            if current and os.path.exists(os.path.join(user_dir, current)):
                return os.path.join(user_dir, current)

        latest = self._latest_history_file(user_dir)
        if latest:
            self._save_state(state_path, os.path.basename(latest))
            return latest

        new_file = self._create_new_history(user_dir)
        self._save_state(state_path, os.path.basename(new_file))
        return new_file

    def open_context(self, user_id: str) -> ConversationContext:
        return ConversationContext(self, self.get_or_create_history(user_id), user_id=user_id)

    def list_histories(self, user_id: str) -> List[str]:
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return []
        names: List[str] = []
        for fname in sorted(os.listdir(user_dir)):
            if not fname.endswith(".json") or fname.endswith("_full.json"):
                continue
            data = self._load_history(os.path.join(user_dir, fname))
            names.append(str(data.get("name", fname)))
        return names

    def switch_history(self, user_id: str, name: str) -> Optional[str]:
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return None

        target: Optional[str] = None
        for fname in os.listdir(user_dir):
            if not fname.endswith(".json") or fname.endswith("_full.json"):
                continue
            path = os.path.join(user_dir, fname)
            data = self._load_history(path)
            if data.get("name") == name or fname == name:
                target = path
                break

        if target:
            self._save_state(os.path.join(user_dir, "state.json"), os.path.basename(target))
        return target

    def set_current_history(self, user_id: str, history_path: str) -> None:
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        self._save_state(os.path.join(user_dir, "state.json"), os.path.basename(history_path))

    def append_message(self, history_path: str, role: str, content: str) -> Dict[str, Any]:
        data = self._load_history(history_path)
        message = {"role": role, "content": content}
        data.setdefault("messages", []).append(self._normalize_message(message))
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        self._append_full_history(history_path, [message])
        if role != "assistant":
            self.maybe_compress(history_path, triggered_by_non_assistant=True)
        return data

    def append_messages(self, history_path: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return self._load_history(history_path)
        data = self._load_history(history_path)
        normalized = [self._normalize_message(dict(msg)) for msg in messages]
        data.setdefault("messages", []).extend(normalized)
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        self._append_full_history(history_path, messages)
        if any(msg.get("role") != "assistant" for msg in normalized):
            self.maybe_compress(history_path, triggered_by_non_assistant=True)
        return data

    def get_message_count(self, history_path: str) -> int:
        return len(self._load_history(history_path).get("messages", []))

    def truncate_history(self, history_path: str, keep_count: int) -> None:
        self._truncate_file(history_path, keep_count)
        self._truncate_file(self._full_history_path(history_path), keep_count)

    def maybe_compress(self, history_path: str, triggered_by_non_assistant: bool) -> bool:
        if not triggered_by_non_assistant:
            return False

        data = self._load_history(history_path)
        messages = data.get("messages", [])
        if self._estimate_tokens(messages) < 60000:
            return False
        if len(messages) <= 3:
            return False

        removed = messages[:-3]
        kept = messages[-3:]
        summary = self._summarize_messages(removed)
        data.setdefault("compressed", []).append(
            {
                "summary": summary,
                "count": len(removed),
                "rounds": self._count_rounds(removed),
                "timestamp": self._timestamp(),
            }
        )
        data["messages"] = [{"role": "user", "content": f"[ContextSummary] {summary}"}] + kept
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        return True

    def create_new_history(self, user_id: str) -> str:
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        new_file = self._create_new_history(user_dir)
        self._save_state(os.path.join(user_dir, "state.json"), os.path.basename(new_file))
        return new_file

    def maybe_rename_after_rounds(self, history_path: str, rounds: int) -> str:
        data = self._load_history(history_path)
        if data.get("renamed"):
            return history_path
        if rounds < 3:
            return history_path

        first_user = ""
        for msg in data.get("messages", []):
            if msg.get("role") == "user":
                first_user = str(msg.get("content", ""))
                break

        ts = data.get("created_at", self._timestamp())
        slug = self._slugify(first_user) or "chat"
        new_name = f"{ts}_{slug}"
        new_path = os.path.join(os.path.dirname(history_path), f"{new_name}.json")

        data["name"] = new_name
        data["renamed"] = True
        self._save_history(history_path, data)

        full_data = self._load_full_history(history_path)
        full_data["name"] = new_name
        full_data["renamed"] = True
        self._save_full_history(history_path, full_data)

        old_full = self._full_history_path(history_path)
        new_full = self._full_history_path(new_path)
        os.rename(history_path, new_path)
        if os.path.exists(old_full):
            os.rename(old_full, new_full)
        return new_path

    def load_messages(self, history_path: str, user_id: Optional[str] = None) -> ConversationContext:
        return ConversationContext(self, history_path, user_id=user_id)

    def get_rounds(self, history_path: str) -> int:
        return int(self._load_history(history_path).get("rounds", 0))

    def get_display_name(self, history_path: str) -> str:
        return str(self._load_history(history_path).get("name", os.path.basename(history_path)))

    def _create_new_history(self, user_dir: str) -> str:
        ts = self._timestamp()
        path = os.path.join(user_dir, f"{ts}.json")
        data = {
            "name": ts,
            "created_at": ts,
            "renamed": False,
            "rounds": 0,
            "messages": [],
        }
        self._save_history(path, data)
        self._save_full_history(path, dict(data))
        return path

    def _load_history(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {"name": os.path.basename(path), "messages": [], "rounds": 0, "renamed": False}
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_history(self, path: str, data: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def _truncate_file(self, path: str, keep_count: int) -> None:
        keep_count = max(0, int(keep_count))
        data = self._load_history(path)
        messages = data.get("messages", [])
        if len(messages) <= keep_count:
            return
        data["messages"] = messages[:keep_count]
        data["rounds"] = self._count_rounds(data["messages"])
        if path.endswith("_full.json"):
            self._save_full_history(path, data)
        else:
            self._save_history(path, data)

    def _save_state(self, path: str, current_file: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"current_file": current_file}, handle, ensure_ascii=False, indent=2)

    def _latest_history_file(self, user_dir: str) -> Optional[str]:
        candidates = [
            os.path.join(user_dir, fname)
            for fname in os.listdir(user_dir)
            if fname.endswith(".json") and not fname.endswith("_full.json")
        ]
        if not candidates:
            return None
        return max(candidates, key=os.path.getmtime)

    def _user_dir(self, user_id: str) -> str:
        return os.path.join(self.base_dir, user_id)

    def _timestamp(self) -> str:
        return time.strftime("%Y%m%d_%H%M%S", time.localtime())

    def _slugify(self, text: str) -> str:
        text = re.sub(r"\s+", "_", (text or "").strip())[:20]
        text = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff-]", "", text)
        return text.strip("_")

    def _count_rounds(self, messages: List[Dict[str, Any]]) -> int:
        user_count = sum(1 for msg in messages if msg.get("role") == "user")
        assistant_count = sum(1 for msg in messages if msg.get("role") == "assistant")
        return min(user_count, assistant_count)

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
        return ContextWindowManager()._fallback_structured_summary(messages)

    def _format_structured_summary(
        self,
        facts: List[str],
        done: List[str],
        todo: List[str],
        constraints: List[str],
        next_steps: List[str],
    ) -> str:
        return ContextWindowManager()._format_structured_summary(facts, done, todo, constraints, next_steps)

    def _estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        total_chars = 0
        for msg in messages:
            total_chars += len(str(msg.get("role", ""))) + 1
            content = msg.get("content")
            if content:
                total_chars += len(str(content))
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                total_chars += len(json.dumps(tool_calls, ensure_ascii=False))
        return math.ceil(total_chars / 4)

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if message.get("role") == "tool" and self.context_manager:
            tool_name = message.get("name") or message.get("tool_name")
            if tool_name == "skill":
                return message
            message["content"] = self.context_manager.normalize_tool_output(message.get("content", ""))
        return message

    def _full_history_path(self, history_path: str) -> str:
        if history_path.endswith("_full.json"):
            return history_path
        base, ext = os.path.splitext(history_path)
        return f"{base}_full{ext}"

    def _load_full_history(self, history_path: str) -> Dict[str, Any]:
        full_path = self._full_history_path(history_path)
        if not os.path.exists(full_path):
            return {"name": os.path.basename(full_path), "messages": [], "rounds": 0, "renamed": False}
        with open(full_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_full_history(self, history_path: str, data: Dict[str, Any]) -> None:
        full_path = self._full_history_path(history_path)
        with open(full_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def _append_full_history(self, history_path: str, messages: List[Dict[str, Any]]) -> None:
        if not messages:
            return

        full_path = self._full_history_path(history_path)
        if os.path.exists(full_path):
            data = self._load_full_history(history_path)
        else:
            base = self._load_history(history_path)
            data = {
                "name": base.get("name", os.path.basename(full_path)),
                "created_at": base.get("created_at", self._timestamp()),
                "renamed": base.get("renamed", False),
                "rounds": 0,
                "messages": [],
            }

        data.setdefault("messages", []).extend(messages)
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_full_history(history_path, data)


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
            "事实: ...\n"
            "已完成: ...\n"
            "未完成/待办: ...\n"
            "约束: ...\n"
            "下一步: ...\n"
            "Do not fabricate facts.\n"
            "Conversation:\n"
            f"{content}"
        )

        response = get_response(
            prompts=[
                {"role": "system", "content": "你是严谨的对话摘要器。"},
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
