# -*- coding: utf-8 -*-
"""编辑文件内容（支持行号与上下文替换）。"""

from __future__ import annotations

from typing import Optional
import os

from tool import Tool
from .path_utils import normalize_root, resolve_relative_path


class EditTool(Tool):
    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="edit",
            description=(
                "Edit a file under agent working directory. "
                "Prefer text replacement by context; line edits are a fallback."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under agent root."},
                    "old_text": {"type": "string", "description": "Text to replace (context-based)."},
                    "new_text": {"type": "string", "description": "Replacement text."},
                    "line_start": {"type": "integer", "description": "1-based start line for line edit."},
                    "line_end": {"type": "integer", "description": "1-based end line for line edit."},
                },
                "required": ["path"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        old_text = kwargs.get("old_text")
        new_text = kwargs.get("new_text") or ""
        line_start = kwargs.get("line_start")
        line_end = kwargs.get("line_end")

        try:
            abs_path = resolve_relative_path(self._agent_root, path)
        except ValueError:
            return "路径不允许或越界。"
        if not os.path.isfile(abs_path):
            return "文件不存在。"

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if old_text:
            if old_text not in content:
                return "未找到需要替换的内容。"
            updated = content.replace(old_text, new_text, 1)
            _write_file(abs_path, updated)
            return "已完成上下文替换。"

        if line_start is None or line_end is None:
            return "请提供 old_text 或者 line_start/line_end。"
        try:
            start = int(line_start)
            end = int(line_end)
        except (TypeError, ValueError):
            return "行号参数无效。"
        if start < 1 or end < start:
            return "行号范围无效。"

        lines = content.splitlines()
        prefix = lines[: start - 1]
        suffix = lines[end:]
        new_lines = new_text.splitlines()
        updated_lines = prefix + new_lines + suffix
        _write_file(abs_path, "\n".join(updated_lines) + ("\n" if content.endswith("\n") else ""))
        return "已完成行号编辑。"


def _write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
