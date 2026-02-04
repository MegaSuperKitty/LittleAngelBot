# -*- coding: utf-8 -*-
"""Skill tool: load a skill prompt as a tool result."""

from typing import Any, Dict, List, Optional

from tool import Tool
from skill_registry import SkillRegistry


class SkillTool(Tool):
    def __init__(self, registry: SkillRegistry, allowed_skills: Optional[List[str]] = None):
        self.registry = registry
        self.allowed_skills = _normalize_allowlist(allowed_skills)
        description = _build_description(registry, self.allowed_skills)
        parameters = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name to load",
                },
            },
            "required": ["name"],
        }
        super().__init__(name="skill", description=description, parameters=parameters)

    def _execute(self, **kwargs):
        name = (kwargs.get("name") or "").strip()
        if not name:
            return "Skill error: name is required."
        if self.allowed_skills is not None and name not in self.allowed_skills:
            return f"Skill not allowed: {name}"
        prompt = self.registry.get_prompt(name)
        if not prompt:
            return f"Skill not found: {name}"
        return prompt


def _build_description(registry: SkillRegistry, allowlist: Optional[List[str]]) -> str:
    skills = registry.list_skills()
    if allowlist is not None:
        allowed = set(allowlist)
        skills = [meta for meta in skills if meta.name in allowed]
    if not skills:
        return "Load a skill prompt by name. No skills available."
    lines = [
        "Load a skill prompt by name.",
        "If the user mentions a specific skill, call this tool first and follow the skill instructions before acting.",
        "Skills are prompts, not executable tools.",
        "Available skills:",
    ]
    for meta in skills:
        desc = meta.description or meta.when_to_use or ""
        if desc:
            lines.append(f"- {meta.name}: {desc}")
        else:
            lines.append(f"- {meta.name}")
    return "\n".join(lines)


def _normalize_allowlist(allowed: Optional[List[str]]) -> Optional[List[str]]:
    if allowed is None:
        return None
    if isinstance(allowed, list):
        cleaned = [str(s).strip() for s in allowed if str(s).strip()]
        return cleaned
    text = str(allowed).strip()
    return [text] if text else []
