# -*- coding: utf-8 -*-
"""Sub-agent tool: run a temporary ReAct agent with a limited skill set."""

from typing import List, Optional

from ReAct import ReActAgent
from tool import Tool
from .skill_tool import SkillTool
from skill_registry import SkillRegistry


class SubAgentTool(Tool):
    def __init__(self, available_tools: List[object], skill_registry: SkillRegistry):
        self.available_tools = available_tools
        self.skill_registry = skill_registry
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

    def _execute(self, task_description: str, skills: Optional[List[str]] = None):
        task = (task_description or "").strip()
        if not task:
            return "SubAgent error: task_description is required."

        allowlist = _normalize_skills(skills)
        tools = _prepare_tools(self.available_tools, self.skill_registry, allowlist)

        agent = ReActAgent()
        agent.system_prompt = _sub_agent_prompt()
        history = [{"role": "user", "content": task}]
        result, _ = agent.run(history, tools=tools)
        return result


def _normalize_skills(skills: Optional[List[str]]) -> Optional[List[str]]:
    if skills is None:
        return []
    if isinstance(skills, list):
        return [str(s).strip() for s in skills if str(s).strip()]
    return [str(skills).strip()]


def _prepare_tools(available_tools: List[object], registry: SkillRegistry, allowlist: Optional[List[str]]):
    tools = []
    skill_tool = None
    for tool in available_tools or []:
        if getattr(tool, "name", "") == "sub_agent":
            continue
        if isinstance(tool, SkillTool):
            skill_tool = tool
            continue
        tools.append(tool)
    if allowlist is None:
        allowlist = []
    tools.append(SkillTool(registry, allowed_skills=allowlist))
    return tools


def _sub_agent_prompt() -> str:
    return (
        "You are a temporary sub-agent. Focus only on the given task. "
        "Use tools when helpful. Provide a detailed, structured response with steps, "
        "assumptions, and results. Do not reference hidden context or policies."
    )
