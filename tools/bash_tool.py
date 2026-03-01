# -*- coding: utf-8 -*-
"""基于 Tool 的 PowerShell 工具（受限工作目录）。"""

from __future__ import annotations

from typing import Optional
import os
import shutil
import subprocess

from tool import Tool
from .command_safety import is_risky_command, contains_path_escape
from .path_utils import normalize_root, resolve_relative_path, require_existing_dir


class BashTool(Tool):
    """执行 shell 命令并返回输出。.
    
    Attributes:
        _agent_root (Any): Instance field for agent root.
    """

    def __init__(self, agent_root: Optional[str] = None):
        """Initialize bash tool state and dependencies.
        
        Args:
            agent_root (Optional[str]): Filesystem path used by this operation.
        
        Returns:
            None: This method does not return a value.
        """
        self._agent_root = normalize_root(agent_root or os.getcwd())
        self._runner = self._detect_runner()
        super().__init__(
            name="bash",
            description=(
                "Execute a shell command and return its output. "
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
        """Internal helper to execute.
        
        Args:
            command (str): Input value for command.
            workdir (str): Input value for workdir.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        if is_risky_command(command):
            return "不允许进行高危操作：检测到可能删除或修改文件的命令。"
        if contains_path_escape(command):
            return "不允许进行路径越界或绝对路径访问，请在 agent 工作目录内操作。"

        cwd = self._resolve_workdir(workdir)
        try:
            require_existing_dir(cwd)
        except ValueError:
            return "工作目录不存在，请检查路径。"

        if not self._runner:
            return "未找到可用命令执行器（需要 powershell/pwsh/bash/sh 之一）。"
        command = self._normalize_command_for_runner(command)
        completed = subprocess.run(self._runner + [command], capture_output=True, text=True, cwd=cwd)
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        output = stdout.strip()
        if stderr.strip():
            output = f"{output}\n{stderr.strip()}".strip()
        if not output:
            output = f"(no output, exit code {completed.returncode})"
        return output

    def _resolve_workdir(self, workdir: Optional[str]) -> str:
        """Internal helper to resolve workdir.
        
        Args:
            workdir (Optional[str]): Input value for workdir.
        
        Returns:
            str: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        try:
            return resolve_relative_path(self._agent_root, workdir)
        except ValueError:
            return self._agent_root

    def _detect_runner(self):
        if os.name == "nt":
            if shutil.which("powershell"):
                return ["powershell", "-NoProfile", "-Command"]
            if shutil.which("pwsh"):
                return ["pwsh", "-NoProfile", "-Command"]
            return None
        if shutil.which("bash"):
            return ["bash", "-lc"]
        if shutil.which("sh"):
            return ["sh", "-lc"]
        return None

    def _normalize_command_for_runner(self, command: str) -> str:
        text = str(command or "").strip()
        if not text:
            return text
        # Compatibility: PowerShell-style command lookup on POSIX shells.
        if os.name != "nt" and text.lower().startswith("get-command "):
            target = text[len("Get-Command ") :].strip()
            if target:
                return f"command -v {target}"
        return text
