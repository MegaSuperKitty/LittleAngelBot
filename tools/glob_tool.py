# -*- coding: utf-8 -*-
"""按模式查找文件。"""

from __future__ import annotations

from typing import Optional
import glob
import os

from tool import Tool
from .path_utils import normalize_root, resolve_relative_path, is_within_base


class GlobTool(Tool):
    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="glob",
            description="Find files by glob pattern under agent working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern relative to agent root."},
                    "max_results": {"type": "integer", "description": "Maximum results to return."},
                },
                "required": ["pattern"],
            },
        )

    def _execute(self, **kwargs):
        pattern = (kwargs.get("pattern") or "").strip()
        max_results = int(kwargs.get("max_results") or 200)
        if not pattern:
            return "pattern 不能为空。"
        try:
            base = resolve_relative_path(self._agent_root, ".")
        except ValueError:
            return "路径不允许或越界。"
        full_pattern = os.path.join(base, pattern)
        results = glob.glob(full_pattern, recursive=True)
        filtered = []
        for path in results:
            if not is_within_base(path, base):
                continue
            rel = os.path.relpath(path, base)
            filtered.append(rel)
            if len(filtered) >= max_results:
                break
        if not filtered:
            return "未找到匹配项。"
        return "\n".join(filtered)
