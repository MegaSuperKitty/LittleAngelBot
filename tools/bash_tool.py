# -*- coding: utf-8 -*-
"""基于 Tool 的 PowerShell 工具（受限工作目录）。"""

from __future__ import annotations

from typing import Optional
import os
import subprocess

from tool import Tool
from .command_safety import is_risky_command, contains_path_escape
from .path_utils import normalize_root, resolve_relative_path, require_existing_dir


class BashTool(Tool):
    """执行 PowerShell 命令并返回输出。"""

    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="bash",
            description=(
                "Execute a PowerShell command and return its output. "
                "All paths are resolved under the agent working directory."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute.",
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Optional working directory (relative to agent root).",
                    },
                },
                "required": ["command"],
            },
        )

    def _execute(self, command: str, workdir: str = None):
        if is_risky_command(command):
            return "不允许进行高危操作：检测到可能删除或修改文件的命令。"
        if contains_path_escape(command):
            return "不允许进行路径越界或绝对路径访问，请在 agent 工作目录内操作。"

        cwd = self._resolve_workdir(workdir)
        try:
            require_existing_dir(cwd)
        except ValueError:
            return "工作目录不存在，请检查路径。"

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        output = stdout.strip()
        if stderr.strip():
            output = f"{output}\n{stderr.strip()}".strip()
        if not output:
            output = f"(no output, exit code {completed.returncode})"
        return output

    def _resolve_workdir(self, workdir: Optional[str]) -> str:
        try:
            return resolve_relative_path(self._agent_root, workdir)
        except ValueError:
            return self._agent_root
