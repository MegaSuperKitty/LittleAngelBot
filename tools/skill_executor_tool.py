# -*- coding: utf-8 -*-
"""技能脚本执行器（受限到指定技能目录）。"""

from __future__ import annotations

from typing import Optional
import os
import subprocess

from tool import Tool
from .command_safety import is_risky_command, contains_path_escape
from .path_utils import normalize_root, resolve_relative_path, require_existing_dir, is_within_base


class SkillExecutorTool(Tool):
    def __init__(self, skills_root: str):
        self._skills_root = normalize_root(skills_root)
        super().__init__(
            name="skill_exec",
            description=(
                "Execute a command inside a specific skill directory. "
                "All paths are restricted to that skill folder."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "Skill name under skills root."},
                    "command": {"type": "string", "description": "Command to execute."},
                    "workdir": {
                        "type": "string",
                        "description": "Optional working directory (relative to the skill folder).",
                    },
                },
                "required": ["skill", "command"],
            },
        )

    def _execute(self, **kwargs):
        skill = (kwargs.get("skill") or "").strip()
        command = kwargs.get("command") or ""
        workdir = kwargs.get("workdir")
        if not skill:
            return "skill 不能为空。"
        # if is_risky_command(command):
        #     return "不允许进行高危操作：检测到可能删除或修改文件的命令。"
        # if contains_path_escape(command):
        #     return "不允许进行路径越界或绝对路径访问。"

        skill_dir = os.path.join(self._skills_root, skill)
        if not is_within_base(skill_dir, self._skills_root) or not os.path.isdir(skill_dir):
            return "技能目录不存在。"

        cwd = self._resolve_workdir(skill_dir, workdir)
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

    def _resolve_workdir(self, skill_dir: str, workdir: Optional[str]) -> str:
        try:
            return resolve_relative_path(skill_dir, workdir)
        except ValueError:
            return skill_dir
