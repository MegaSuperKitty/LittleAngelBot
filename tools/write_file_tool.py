# -*- coding: utf-8 -*-
"""Write file contents under agent working directory."""

from __future__ import annotations

from typing import Optional
import os

from tool import Tool
from .path_utils import normalize_root, resolve_relative_path


class WriteFileTool(Tool):
    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="write_file",
            description=(
                "Create a new file under the agent working directory. "
                "Will not overwrite existing files; use edit for modifications. "
                "Paths are restricted to the agent root."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under agent root."},
                    "content": {"type": "string", "description": "Full file content to write."},
                },
                "required": ["path", "content"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        content = kwargs.get("content") or ""
        try:
            abs_path = resolve_relative_path(self._agent_root, path)
        except ValueError:
            return "路径不允许或越界。"

        if os.path.exists(abs_path):
            return "文件已存在，请使用 edit 工具修改。"

        parent = os.path.dirname(abs_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return "已写入文件。"
