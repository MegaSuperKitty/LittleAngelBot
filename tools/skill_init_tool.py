# -*- coding: utf-8 -*-
"""Skill initializer tool: create a new skill directory under ./skills."""

from __future__ import annotations

from typing import Optional
import os
import re
import subprocess
import sys

from tool import Tool


_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SkillInitTool(Tool):
    def __init__(self, skills_root: str):
        self._skills_root = os.path.abspath(skills_root)
        self._script_path = os.path.join(
            self._skills_root, "skill-creator", "scripts", "init_skill.py"
        )
        super().__init__(
            name="skill_init",
            description=(
                "Initialize a new skill folder under ./skills using the skill-creator template. "
                "Provide the skill name only (lowercase letters/numbers with hyphens)."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Skill name, e.g. my-new-skill",
                    }
                },
                "required": ["skill_name"],
            },
        )

    def _execute(self, **kwargs):
        skill_name = (kwargs.get("skill_name") or "").strip()
        if not skill_name:
            return "skill_name 不能为空。"
        if not _SKILL_NAME_RE.match(skill_name):
            return "skill_name 必须是小写字母/数字，使用连字符分隔（例如 my-new-skill）。"

        if not os.path.isfile(self._script_path):
            return "init_skill.py 不存在，无法初始化技能。"

        target_dir = os.path.join(self._skills_root, skill_name)
        if os.path.exists(target_dir):
            return f"技能目录已存在：{target_dir}"

        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    self._script_path,
                    skill_name,
                    "--path",
                    self._skills_root,
                ],
                capture_output=True,
                text=True,
                cwd=self._skills_root,
            )
        except Exception as exc:
            return f"初始化失败：{exc}"

        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        output = "\n".join(x for x in [stdout, stderr] if x).strip()
        if not output:
            output = f"(no output, exit code {completed.returncode})"

        hint = (
            "\n\n后续操作提示：\n"
            "你可以使用 skill_exec 工具，并将 skill 设为刚创建的技能名，"
            "在该技能目录内创建/编辑 SKILL.md，以及 scripts/、references/ 等资源。\n"
            "例如：\n"
            "1) skill_exec {skill: \""
            + skill_name
            + "\", command: \"New-Item -ItemType Directory -Path references\"}\n"
            "2) skill_exec {skill: \""
            + skill_name
            + "\", command: \"New-Item -ItemType Directory -Path scripts\"}\n"
            "3) skill_exec {skill: \""
            + skill_name
            + "\", command: \"Set-Content -Path SKILL.md -Value '<your content>'\"}"
        )
        return output + hint
