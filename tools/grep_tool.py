# -*- coding: utf-8 -*-
"""在文件中搜索文本。"""

from __future__ import annotations

from typing import Optional
import os

from tool import Tool
from .path_utils import normalize_root, resolve_relative_path, is_within_base


class GrepTool(Tool):
    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="grep",
            description="Search for text in files under agent working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Text to search for."},
                    "path": {"type": "string", "description": "Relative file or directory path."},
                    "max_matches": {"type": "integer", "description": "Maximum matches to return."},
                },
                "required": ["pattern"],
            },
        )

    def _execute(self, **kwargs):
        pattern = (kwargs.get("pattern") or "")
        target = (kwargs.get("path") or ".").strip()
        max_matches = int(kwargs.get("max_matches") or 200)
        if not pattern:
            return "pattern 不能为空。"
        try:
            base = resolve_relative_path(self._agent_root, ".")
            abs_target = resolve_relative_path(self._agent_root, target)
        except ValueError:
            return "路径不允许或越界。"
        matches = []
        if os.path.isfile(abs_target):
            _scan_file(abs_target, base, pattern, matches, max_matches)
        else:
            for root, _, files in os.walk(abs_target):
                if not is_within_base(root, base):
                    continue
                for name in files:
                    path = os.path.join(root, name)
                    _scan_file(path, base, pattern, matches, max_matches)
                    if len(matches) >= max_matches:
                        break
                if len(matches) >= max_matches:
                    break
        if not matches:
            return "未找到匹配项。"
        return "\n".join(matches)


def _scan_file(path: str, base: str, pattern: str, out: list, limit: int) -> None:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, start=1):
                if pattern in line:
                    rel = os.path.relpath(path, base)
                    out.append(f"{rel}:{idx}: {line.rstrip()}")
                    if len(out) >= limit:
                        return
    except (OSError, UnicodeError):
        return
