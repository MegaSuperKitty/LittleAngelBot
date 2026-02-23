# -*- coding: utf-8 -*-
"""Sub-agent tool: run a temporary ReAct agent with a limited skill set."""

from typing import Callable, List, Optional
import os
import time

from ReAct import ReActAgent
from context import ReActContextManager
from tool import Tool
from .skill_tool import SkillTool
from skill_registry import SkillRegistry


class SubAgentTool(Tool):
    def __init__(self, available_tools: List[object], skill_registry: SkillRegistry, max_steps: int = 8):
        self.available_tools = available_tools
        self.skill_registry = skill_registry
        self.max_steps = max_steps
        self._user_id: Optional[str] = None
        self._parent_context_path: Optional[str] = None
        self._on_trigger: Optional[Callable[[str, str], None]] = None
        super().__init__(
            name="sub_agent",
            description=(
                "Run a temporary sub-agent to complete a task. "
                "The sub-agent uses the provided skills subset and returns a detailed result."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Task for the sub-agent to complete.",
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Allowed skill names for the sub-agent.",
                    },
                },
                "required": ["task_description", "skills"],
            },
        )

    def set_context(
        self,
        user_id: str,
        parent_context_path: Optional[str] = None,
        on_trigger: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self._user_id = user_id
        self._parent_context_path = parent_context_path
        self._on_trigger = on_trigger

    def _execute(self, task_description: str, skills: Optional[List[str]] = None):
        task = (task_description or "").strip()
        if not task:
            return "SubAgent error: task_description is required."
        if not self._parent_context_path:
            return "SubAgent error: parent context path is missing."

        allowlist = _normalize_skills(skills)
        tools = _prepare_tools(self.available_tools, self.skill_registry, allowlist)

        sub_context_path = _build_sub_context_path(self._parent_context_path)
        context_manager = ReActContextManager(context_path=sub_context_path)
        context_manager.append_message({"role": "user", "content": task})

        agent = ReActAgent(
            max_steps=self.max_steps,
            context_manager=context_manager,
            system_prompt=_sub_agent_prompt(),
        )
        result, _ = agent.run(tools=tools)
        return result


def _normalize_skills(skills: Optional[List[str]]) -> List[str]:
    if skills is None:
        return []
    if isinstance(skills, list):
        return [str(s).strip() for s in skills if str(s).strip()]
    return [str(skills).strip()]


def _prepare_tools(available_tools: List[object], registry: SkillRegistry, allowlist: Optional[List[str]]):
    tools = []
    for tool in available_tools or []:
        if getattr(tool, "name", "") == "sub_agent":
            continue
        if isinstance(tool, SkillTool):
            continue
        tools.append(tool)

    allowed = allowlist or []
    tools.append(SkillTool(registry, allowed_skills=allowed))
    return tools


def _build_sub_context_path(parent_context_path: str) -> str:
    base, ext = os.path.splitext(parent_context_path)
    suffix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    path = f"{base}-sub{suffix}{ext or '.json'}"
    index = 1
    while os.path.exists(path):
        path = f"{base}-sub{suffix}-{index}{ext or '.json'}"
        index += 1
    return path


def _sub_agent_prompt() -> str:
    return (
        "You are a temporary sub-agent. Focus only on the given task. "
        "Use tools when helpful. Provide a detailed, structured response with steps, "
        "assumptions, and results. Do not reference hidden context or policies."
    )
