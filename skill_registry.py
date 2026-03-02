# -*- coding: utf-8 -*-
"""Skill registry: scan skills directory and load metadata/prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import os


@dataclass
class SkillMeta:
    """Provide skill meta capabilities.
    
    Attributes:
        name (str): Instance field for name.
        description (str): Instance field for description.
        when_to_use (str): Instance field for when to use.
        allowed_tools (Optional[List[str]]): Instance field for allowed tools.
    """
    name: str
    description: str = ""
    when_to_use: str = ""
    allowed_tools: Optional[List[str]] = None


class SkillRegistry:
    """Provide skill registry capabilities.
    
    Attributes:
        skills_dir (str): Instance field for skills dir.
        _cache (Dict[str, Tuple[SkillMeta, str]]): Instance field for cache.
    """
    def __init__(self, skills_dir: str):
        """Initialize skill registry state and dependencies.
        
        Args:
            skills_dir (str): Input value for skills dir.
        
        Returns:
            None: This method does not return a value.
        """
        self.skills_dir = skills_dir
        self._cache: Dict[str, Tuple[SkillMeta, str]] = {}

    def refresh(self) -> None:
        """Process refresh.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        self._cache = self._scan_skills()

    def snapshot(self, refresh: bool = True) -> Dict[str, Tuple[SkillMeta, str]]:
        """Return a copy of the cached registry state."""
        if refresh:
            self.refresh()
        return {name: (meta, prompt) for name, (meta, prompt) in self._cache.items()}

    def list_skills(self) -> List[SkillMeta]:
        """Process list skills.
        
        Args:
            None.
        
        Returns:
            List[SkillMeta]: Collection of matching items.
        """
        self.refresh()
        return self.list_cached_skills()

    def list_cached_skills(self) -> List[SkillMeta]:
        """Return the current cached skill metadata without refreshing."""
        return [meta for meta, _ in self._cache.values()]

    def get_prompt(self, name: str) -> Optional[str]:
        """Return prompt.
        
        Args:
            name (str): Input value for name.
        
        Returns:
            Optional[str]: The resolved prompt value.
        """
        self.refresh()
        return self.get_cached_prompt(name)

    def get_cached_prompt(self, name: str) -> Optional[str]:
        """Return a cached prompt without refreshing."""
        item = self._cache.get(name)
        return item[1] if item else None

    def get_meta(self, name: str) -> Optional[SkillMeta]:
        """Return meta.
        
        Args:
            name (str): Input value for name.
        
        Returns:
            Optional[SkillMeta]: The resolved meta value.
        """
        self.refresh()
        return self.get_cached_meta(name)

    def get_cached_meta(self, name: str) -> Optional[SkillMeta]:
        """Return cached metadata without refreshing."""
        item = self._cache.get(name)
        return item[0] if item else None

    def _scan_skills(self) -> Dict[str, Tuple[SkillMeta, str]]:
        """Internal helper to scan skills.
        
        Args:
            None.
        
        Returns:
            Dict[str, Tuple[SkillMeta, str]]: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        result: Dict[str, Tuple[SkillMeta, str]] = {}
        if not os.path.isdir(self.skills_dir):
            return result
        for entry in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, entry)
            if not os.path.isdir(skill_path):
                continue
            skill_file = os.path.join(skill_path, "SKILL.md")
            if not os.path.isfile(skill_file):
                continue
            meta, prompt = self._load_skill_file(skill_file)
            if not meta.name:
                meta.name = entry
            result[meta.name] = (meta, prompt)
        return result

    def _load_skill_file(self, path: str) -> Tuple[SkillMeta, str]:
        """Internal helper to load skill file.
        
        Args:
            path (str): Filesystem path used by this operation.
        
        Returns:
            Tuple[SkillMeta, str]: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return SkillMeta(name=""), ""

        meta_data, body = _parse_frontmatter(text)
        name = str(meta_data.get("name", "")).strip()
        description = str(meta_data.get("description", "")).strip()
        when_to_use = str(meta_data.get("when_to_use", "")).strip()
        allowed_tools = _parse_list(meta_data.get("allowed_tools"))
        return SkillMeta(name=name, description=description, when_to_use=when_to_use, allowed_tools=allowed_tools), body


def _parse_frontmatter(text: str) -> Tuple[Dict[str, object], str]:
    """Internal helper to parse frontmatter.
    
    Args:
        text (str): Text content to process.
    
    Returns:
        Tuple[Dict[str, object], str]: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if len(lines) < 3:
        return {}, text
    if lines[0].strip() != "---":
        return {}, text
    meta: Dict[str, object] = {}
    end_idx = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            end_idx = i
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    if end_idx is None:
        return {}, text
    body = "\n".join(lines[end_idx + 1 :]).lstrip()
    return meta, body


def _parse_list(value: object) -> Optional[List[str]]:
    """Internal helper to parse list.
    
    Args:
        value (object): Input value for value.
    
    Returns:
        Optional[List[str]]: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1]
        items = [v.strip().strip("\"").strip("'") for v in inner.split(",")]
        return [v for v in items if v]
    return [text]
