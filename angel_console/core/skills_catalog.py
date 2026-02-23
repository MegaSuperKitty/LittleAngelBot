# -*- coding: utf-8 -*-
"""Skill catalog reader for the web console."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from skill_registry import SkillRegistry


class SkillsCatalog:
    """Read and shape skill metadata from workspace `skills/` directory."""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir).resolve()
        self.registry = SkillRegistry(str(self.skills_dir))

    def list_skills(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if not self.skills_dir.is_dir():
            return rows

        meta_by_name = {}
        for meta in self.registry.list_skills():
            meta_by_name[meta.name] = meta

        for entry in sorted(self.skills_dir.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_dir():
                continue
            skill_file = entry / "SKILL.md"
            if not skill_file.is_file():
                continue

            meta = meta_by_name.get(entry.name)
            name = entry.name
            description = ""
            if meta is not None:
                if meta.name:
                    name = meta.name
                description = meta.description or ""

            rows.append(
                {
                    "name": name,
                    "directory": entry.name,
                    "description": description,
                    "path": str(entry.resolve()),
                }
            )
        return rows
