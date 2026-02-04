# -*- coding: utf-8 -*-
"""读取文件内容并带行号输出。"""

from __future__ import annotations

from typing import Optional
import os

from tool import Tool
from .path_utils import normalize_root, resolve_relative_path


class ReadTool(Tool):
    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="read",
            description="Read a text file with line numbers (agent working directory only).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under agent root."},
                    "start_line": {"type": "integer", "description": "Start line (1-based)."},
                    "end_line": {"type": "integer", "description": "End line (1-based)."},
                    "max_lines": {"type": "integer", "description": "Maximum lines to return (capped at 100)."},
                },
                "required": ["path"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        start_line = int(kwargs.get("start_line") or 1)
        end_line = kwargs.get("end_line")
        max_lines = int(kwargs.get("max_lines") or 200)
        if max_lines > 100:
            max_lines = 100
        try:
            abs_path = resolve_relative_path(self._agent_root, path)
        except ValueError:
            return "路径不允许或越界。"
        if not os.path.isfile(abs_path):
            return "文件不存在。"
        if start_line < 1:
            start_line = 1
        lines = []
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, start=1):
                if idx < start_line:
                    continue
                if end_line is not None and idx > int(end_line):
                    break
                lines.append(f"{idx:>6}: {line.rstrip()}")
                if len(lines) >= max_lines:
                    break
        if not lines:
            return "没有可展示的内容。"
        return "\n".join(lines)
