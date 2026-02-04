from typing import Dict, List, Optional
import json
import os
import re
import time
import math
from openai import OpenAI


class ContextWindowManager:
    """Handle sliding window and long tool output normalization for messages."""

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

    def estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        total_chars = 0
        for msg in messages:
            total_chars += len(msg.get("role", "")) + 1
            content = msg.get("content", "")
            if content:
                total_chars += len(str(content))
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                total_chars += len(json.dumps(tool_calls, ensure_ascii=False))
        return math.ceil(total_chars / 4)

    def window_messages(self, messages: List[Dict[str, str]], preserve_system: bool = True) -> List[Dict[str, str]]:
        if not messages:
            return []
        if self.estimate_tokens(messages) <= self.max_tokens:
            return list(messages)

        start_idx = 0
        system_msg: List[Dict[str, str]] = []
        if preserve_system and messages[0].get("role") == "system":
            start_idx = 1
            system_msg = [messages[0]]

        body = messages[start_idx:]
        if not body:
            return list(messages)

        keep = body[-self.min_keep:]
        window = system_msg + keep
        while self.estimate_tokens(window) > self.max_tokens and len(keep) > 1:
            keep = keep[1:]
            window = system_msg + keep
        return window

    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        summarizer=None,
        preserve_system: bool = True,
        triggered_by_non_assistant: bool = True,
    ) -> List[Dict[str, str]]:
        if not messages:
            return []
        if not triggered_by_non_assistant:
            return list(messages)
        if self.estimate_tokens(messages) < self.max_tokens:
            return list(messages)

        start_idx = 0
        system_msg: List[Dict[str, str]] = []
        if preserve_system and messages[0].get("role") == "system":
            start_idx = 1
            system_msg = [messages[0]]

        body = messages[start_idx:]
        if len(body) <= 3:
            return list(messages)

        removed = body[:-3]
        kept = body[-3:]
        summary = self._summarize_messages(removed, summarizer)
        summary_msg = {"role": "user", "content": f"【ContextSummary】{summary}"}
        return system_msg + [summary_msg] + kept

    def _summarize_messages(self, messages: List[Dict[str, str]], summarizer=None) -> str:
        if summarizer:
            try:
                summary = summarizer.summarize(messages)
                if summary:
                    return summary.strip()
            except Exception:
                pass
        return self._fallback_structured_summary(messages)

    def _fallback_structured_summary(self, messages: List[Dict[str, str]]) -> str:
        if not messages:
            return self._format_structured_summary(
                facts=["无"],
                done=["未明确"],
                todo=["未明确"],
                constraints=["未明确"],
                next_steps=["无"],
            )

        facts = []
        done = []
        todo = []
        constraints = []

        for msg in messages:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip().replace("\n", " ")
            if not content:
                continue
            content = content[:120] + ("..." if len(content) > 120 else "")

            if role == "user" and len(facts) < 3:
                facts.append(content)

            if role == "assistant":
                if any(k in content for k in ["已完成", "完成", "实现", "修复", "新增", "更新", "改为"]):
                    if len(done) < 3:
                        done.append(content)

            if any(k in content for k in ["需要", "请", "想要", "得", "下一步", "TODO"]):
                if len(todo) < 3:
                    todo.append(content)

            if any(k in content for k in ["不要", "必须", "不", "不能", "限制", "要求", "注意"]):
                if len(constraints) < 3:
                    constraints.append(content)

        if not facts:
            facts = ["未明确"]
        if not done:
            done = ["未明确"]
        if not todo:
            todo = ["未明确"]
        if not constraints:
            constraints = ["未明确"]

        next_steps = todo[:2] if todo else ["未明确"]
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
            "事实: " + "；".join(facts) + "\n"
            "已完成: " + "；".join(done) + "\n"
            "未完成/待办: " + "；".join(todo) + "\n"
            "约束: " + "；".join(constraints) + "\n"
            "下一步: " + "；".join(next_steps)
        )

    def normalize_tool_output(self, content: str) -> str:
        if content is None:
            return ""
        if not isinstance(content, str):
            content = str(content)
        if len(content) <= 10000:
            return content
        if content.startswith("该工具的返回结果因为超长被放到了"):
            return content

        output_path = self._write_tool_output(content)
        if output_path:
            if self.agent_root:
                rel_path = os.path.relpath(output_path, self.agent_root)
            else:
                rel_path = output_path
            prefix = (
                f"该工具的返回结果因为超长被放到了（{rel_path}）下，你需要完整内容请用read工具进行读取，现在只展示前1000个字符："
            )
        else:
            prefix = "该工具的返回结果因为超长被放到了（未知路径）下，你需要完整内容请用read工具进行读取，现在只展示前1000个字符："
        return prefix + content[:1000]

    def _write_tool_output(self, content: str) -> Optional[str]:
        if not self.tool_output_dir:
            return None
        os.makedirs(self.tool_output_dir, exist_ok=True)
        self._tool_output_index += 1
        filename = f"tool_output_{time.strftime('%Y%m%d_%H%M%S')}_{self._tool_output_index}.txt"
        path = os.path.join(self.tool_output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return path
        except Exception:
            return None


class ConversationContext:
    """In-memory context wrapper for a single conversation session."""

    def __init__(self, history_manager: "HistoryManager", history_path: str, user_id: Optional[str] = None):
        self._history_manager = history_manager
        self.history_path = history_path
        self.user_id = user_id
        self._runtime_messages: Optional[List[Dict[str, str]]] = None
        self._messages: List[Dict[str, str]] = []
        self._baseline_count = 0
        self._reload()
        self._baseline_count = len(self._messages)

    def _reload(self) -> None:
        data = self._history_manager._load_history(self.history_path)
        self._messages = data.get("messages", [])

    def get_messages(self) -> List[Dict[str, str]]:
        return self._runtime_messages if self._runtime_messages is not None else self._messages

    def get_history_messages(self) -> List[Dict[str, str]]:
        return self._messages

    def set_runtime_messages(self, messages: List[Dict[str, str]]) -> None:
        self._runtime_messages = messages

    def clear_runtime_messages(self) -> None:
        self._runtime_messages = None

    def append_message(self, role: str, content: str) -> None:
        self._history_manager.append_message(self.history_path, role, content)
        self._reload()
        self.clear_runtime_messages()

    def append_messages(self, messages: List[Dict[str, str]]) -> None:
        self._history_manager.append_messages(self.history_path, messages)
        self._reload()
        self.clear_runtime_messages()

    def rollback(self) -> None:
        self._history_manager.truncate_history(self.history_path, self._baseline_count)
        self._reload()
        self.clear_runtime_messages()

    def finalize(self) -> str:
        new_path = self._history_manager.maybe_rename_after_rounds(
            self.history_path, self._history_manager.get_rounds(self.history_path)
        )
        if new_path != self.history_path:
            self.history_path = new_path
            if self.user_id:
                self._history_manager.set_current_history(self.user_id, new_path)
        return self.history_path

class HistoryManager:
    """本地对话历史管理（按用户隔离、支持压缩与命名）。"""

    def __init__(
        self,
        base_dir: str,
        max_rounds: int = 100,
        summarizer=None,
        context_manager: Optional[ContextWindowManager] = None,
    ):
        """初始化历史管理器。

        Args:
            base_dir: 历史根目录。
            max_rounds: 达到该轮数则触发压缩。
            summarizer: 可选的摘要器（需实现 summarize(messages)）。
        """
        self.base_dir = base_dir
        self.max_rounds = max_rounds
        self.summarizer = summarizer
        self.context_manager = context_manager
        os.makedirs(self.base_dir, exist_ok=True)

    def get_or_create_history(self, user_id: str):
        """获取当前历史文件路径；不存在则创建。"""
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        state_path = os.path.join(user_dir, "state.json")

        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
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
        """Open a conversation context for a user (load history + bind user_id)."""
        history_path = self.get_or_create_history(user_id)
        return ConversationContext(self, history_path, user_id=user_id)

    def list_histories(self, user_id: str) -> List[str]:
        """列出用户所有历史的显示名。"""
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return []
        names = []
        for fname in sorted(os.listdir(user_dir)):
            if not fname.endswith(".json") or fname.endswith("_full.json"):
                continue
            path = os.path.join(user_dir, fname)
            data = self._load_history(path)
            names.append(data.get("name", fname))
        return names

    def switch_history(self, user_id: str, name: str) -> Optional[str]:
        """按显示名或文件名切换历史。"""
        user_dir = self._user_dir(user_id)
        if not os.path.exists(user_dir):
            return None
        target = None
        for fname in os.listdir(user_dir):
            if not fname.endswith(".json") or fname.endswith("_full.json"):
                continue
            path = os.path.join(user_dir, fname)
            data = self._load_history(path)
            if data.get("name") == name or fname == name:
                target = path
                break
        if target:
            state_path = os.path.join(user_dir, "state.json")
            self._save_state(state_path, os.path.basename(target))
        return target

    def set_current_history(self, user_id: str, history_path: str):
        """显式设置当前历史文件（写入 state.json）。"""
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        state_path = os.path.join(user_dir, "state.json")
        self._save_state(state_path, os.path.basename(history_path))

    def append_message(self, history_path: str, role: str, content: str):
        """追加一条消息并更新轮数统计。"""
        data = self._load_history(history_path)
        message = {"role": role, "content": content}
        data.setdefault("messages", []).append(self._normalize_message(message))
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        self._append_full_history(history_path, [message])
        if role != "assistant":
            self.maybe_compress(history_path, triggered_by_non_assistant=True)
        return data

    def append_messages(self, history_path: str, messages: List[Dict[str, str]]):
        """追加多条消息并更新轮数统计。"""
        if not messages:
            return self._load_history(history_path)
        data = self._load_history(history_path)
        normalized = [self._normalize_message(dict(m)) for m in messages]
        data.setdefault("messages", []).extend(normalized)
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        self._append_full_history(history_path, messages)
        if any(m.get("role") != "assistant" for m in normalized):
            self.maybe_compress(history_path, triggered_by_non_assistant=True)
        return data

    def get_message_count(self, history_path: str) -> int:
        """获取当前历史消息数量。"""
        data = self._load_history(history_path)
        return len(data.get("messages", []))

    def truncate_history(self, history_path: str, keep_count: int) -> None:
        """截断历史到指定消息数量（同时截断 full 记录）。"""
        self._truncate_file(history_path, keep_count)
        self._truncate_file(self._full_history_path(history_path), keep_count)

    def maybe_compress(self, history_path: str, triggered_by_non_assistant: bool) -> bool:
        """插入非 assistant 消息后，若 token 数达到阈值则压缩上下文。"""
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
        data["messages"] = [{"role": "user", "content": f"【ContextSummary】{summary}"}] + kept
        data["rounds"] = self._count_rounds(data["messages"])
        self._save_history(history_path, data)
        return True

    def create_new_history(self, user_id: str) -> str:
        """显式新建历史文件并设置为当前历史。"""
        user_dir = self._user_dir(user_id)
        os.makedirs(user_dir, exist_ok=True)
        new_file = self._create_new_history(user_dir)
        state_path = os.path.join(user_dir, "state.json")
        self._save_state(state_path, os.path.basename(new_file))
        return new_file

    def maybe_rename_after_rounds(self, history_path: str, rounds: int):
        """对话达到 3 轮后重命名历史文件。"""
        data = self._load_history(history_path)
        if data.get("renamed"):
            return history_path
        if rounds < 3:
            return history_path

        first_user = ""
        for msg in data.get("messages", []):
            if msg.get("role") == "user":
                first_user = msg.get("content", "")
                break

        ts = data.get("created_at", self._timestamp())
        slug = self._slugify(first_user) or "chat"
        new_name = f"{ts}_{slug}"
        new_fname = f"{new_name}.json"
        new_path = os.path.join(os.path.dirname(history_path), new_fname)

        data["name"] = new_name
        data["renamed"] = True
        self._save_history(history_path, data)
        full_data = self._load_full_history(history_path)
        full_data["name"] = new_name
        full_data["renamed"] = True
        self._save_full_history(history_path, full_data)
        full_old = self._full_history_path(history_path)
        full_new = self._full_history_path(new_path)
        os.rename(history_path, new_path)
        if os.path.exists(full_old):
            os.rename(full_old, full_new)
        return new_path

    def load_messages(self, history_path: str, user_id: Optional[str] = None) -> ConversationContext:
        """Return a ConversationContext for the given history path."""
        return ConversationContext(self, history_path, user_id=user_id)

    def get_rounds(self, history_path: str) -> int:
        """获取当前历史轮数。"""
        data = self._load_history(history_path)
        return data.get("rounds", 0)

    def get_display_name(self, history_path: str) -> str:
        """获取历史显示名（name 字段或文件名）。"""
        data = self._load_history(history_path)
        return data.get("name", os.path.basename(history_path))

    def _create_new_history(self, user_dir: str) -> str:
        """新建历史文件，初始名称为时间戳。"""
        ts = self._timestamp()
        name = ts
        fname = f"{name}.json"
        path = os.path.join(user_dir, fname)
        data = {
            "name": name,
            "created_at": ts,
            "renamed": False,
            "rounds": 0,
            "messages": [],
        }
        self._save_history(path, data)
        self._save_full_history(path, dict(data))
        return path

    def _load_history(self, path: str) -> Dict:
        """读取历史文件；若不存在则返回空结构。"""
        if not os.path.exists(path):
            return {"name": os.path.basename(path), "messages": [], "rounds": 0, "renamed": False}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_history(self, path: str, data: Dict):
        """保存历史文件（UTF-8，保留中文）。"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def _truncate_file(self, path: str, keep_count: int) -> None:
        if keep_count < 0:
            keep_count = 0
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

    def _save_state(self, path: str, current_file: str):
        """保存当前历史指针。"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"current_file": current_file}, f, ensure_ascii=False, indent=2)

    def _latest_history_file(self, user_dir: str) -> Optional[str]:
        """取最近修改时间的历史文件作为默认恢复目标。"""
        candidates = [
            os.path.join(user_dir, f)
            for f in os.listdir(user_dir)
            if f.endswith(".json") and not f.endswith("_full.json")
        ]
        if not candidates:
            return None
        return max(candidates, key=os.path.getmtime)

    def _user_dir(self, user_id: str) -> str:
        """获取用户对应的历史目录。"""
        return os.path.join(self.base_dir, user_id)

    def _timestamp(self) -> str:
        """生成统一时间戳字符串。"""
        return time.strftime("%Y%m%d_%H%M%S", time.localtime())

    def _slugify(self, text: str) -> str:
        """把文本转换为适合作为文件名的短标题。"""
        text = re.sub(r"\s+", "_", text.strip())[:20]
        text = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff-]", "", text)
        return text.strip("_")

    def _count_rounds(self, messages: List[Dict[str, str]]) -> int:
        """以用户/助手消息对数作为轮数。"""
        user_count = sum(1 for m in messages if m.get("role") == "user")
        assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
        return min(user_count, assistant_count)

    def _summarize_messages(self, messages: List[Dict[str, str]]) -> str:
        """将旧消息压缩为简短摘要。"""
        if self.summarizer:
            try:
                summary = self.summarizer.summarize(messages)
                if summary:
                    return summary.strip()
            except Exception:
                pass
        return self._fallback_structured_summary(messages)

    def _fallback_structured_summary(self, messages: List[Dict[str, str]]) -> str:
        if not messages:
            return self._format_structured_summary(
                facts=["无"],
                done=["未明确"],
                todo=["未明确"],
                constraints=["未明确"],
                next_steps=["无"],
            )

        facts = []
        done = []
        todo = []
        constraints = []

        for msg in messages:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip().replace("\n", " ")
            if not content:
                continue
            content = content[:120] + ("..." if len(content) > 120 else "")

            if role == "user" and len(facts) < 3:
                facts.append(content)

            if role == "assistant":
                if any(k in content for k in ["已完成", "完成", "实现", "修复", "新增", "更新", "改为"]):
                    if len(done) < 3:
                        done.append(content)

            if any(k in content for k in ["需要", "请", "想要", "待", "下一步", "TODO"]):
                if len(todo) < 3:
                    todo.append(content)

            if any(k in content for k in ["不要", "必须", "仅", "不能", "限制", "要求", "注意"]):
                if len(constraints) < 3:
                    constraints.append(content)

        if not facts:
            facts = ["未明确"]
        if not done:
            done = ["未明确"]
        if not todo:
            todo = ["未明确"]
        if not constraints:
            constraints = ["未明确"]

        next_steps = todo[:2] if todo else ["未明确"]
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
            "事实: " + "；".join(facts) + "\n"
            "已完成: " + "；".join(done) + "\n"
            "未完成/待办: " + "；".join(todo) + "\n"
            "约束: " + "；".join(constraints) + "\n"
            "下一步: " + "；".join(next_steps)
        )

    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """估算消息列表的 token 数量（粗略）。"""
        total_chars = 0
        for msg in messages:
            total_chars += len(msg.get("role", "")) + 1
            content = msg.get("content", "")
            if content:
                total_chars += len(str(content))
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                total_chars += len(json.dumps(tool_calls, ensure_ascii=False))
        return math.ceil(total_chars / 4)


    def _normalize_message(self, message: Dict[str, str]) -> Dict[str, str]:
        if message.get("role") == "tool" and self.context_manager:
            tool_name = message.get("name") or message.get("tool_name")
            if tool_name == "skill":
                return message
            content = message.get("content", "")
            message["content"] = self.context_manager.normalize_tool_output(content)
        return message

    def _full_history_path(self, history_path: str) -> str:
        if history_path.endswith("_full.json"):
            return history_path
        base, ext = os.path.splitext(history_path)
        return f"{base}_full{ext}"

    def _load_full_history(self, history_path: str) -> Dict:
        full_path = self._full_history_path(history_path)
        if not os.path.exists(full_path):
            return {"name": os.path.basename(full_path), "messages": [], "rounds": 0, "renamed": False}
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_full_history(self, history_path: str, data: Dict) -> None:
        full_path = self._full_history_path(history_path)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _append_full_history(self, history_path: str, messages: List[Dict[str, str]]) -> None:
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
    """基于 LLM 的对话摘要器。"""

    def __init__(
        self,
        model: str = "qwen-max",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_chars: int = 500,
    ):
        self.model = model
        self.base_url = base_url or os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
        self.max_output_chars = max_output_chars
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def summarize(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表压缩成结构化中文摘要。"""
        if not messages:
            return (
                "事实: 无\n"
                "已完成: 未明确\n"
                "未完成/待办: 未明确\n"
                "约束: 未明确\n"
                "下一步: 无"
            )
        content = self._format_messages(messages, max_chars=4000)
        prompt = (
            "请用中文将对话压缩为结构化摘要，要求：\n"
            "- 保留关键事实、决策、任务、约束与未完成事项\n"
            "- 明确写出“已完成”的事项\n"
            "- 不要编造信息\n"
            "- 严格按以下格式输出，每行一个字段，不要附加其他文字：\n"
            "事实: ...\n"
            "已完成: ...\n"
            "未完成/待办: ...\n"
            "约束: ...\n"
            "下一步: ...\n"
            "对话内容如下：\n"
            f"{content}"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个严谨的对话摘要器。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            top_p=0.1,
        )
        text = (response.choices[0].message.content or "").strip()
        if self.max_output_chars and len(text) > self.max_output_chars:
            text = text[: self.max_output_chars].rstrip() + "..."
        return text

    def _format_messages(self, messages: List[Dict[str, str]], max_chars: int = 4000) -> str:
        parts = []
        total = 0
        for msg in messages:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip().replace("\n", " ")
            line = f"{role}: {content}"
            parts.append(line)
            total += len(line) + 1
            if total >= max_chars:
                break
        text = "\n".join(parts)
        if total >= max_chars:
            text += "\n..."
        return text
