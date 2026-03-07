# -*- coding: utf-8 -*-
"""Built-in local MCP server implementations backed by existing tool logic."""

from __future__ import annotations

import os
from typing import List

from mcp.schema import MCPServerManifest

from mcp.local_tools.alarm_tool import AlarmTool
from mcp.local_tools.ask_human_tool import AskHumanTool
from mcp.local_tools.bash_tool import BashTool
from mcp.local_tools.cite_manager_tool import CiteManagerTool
from mcp.local_tools.edit_tool import EditTool
from mcp.local_tools.glob_tool import GlobTool
from mcp.local_tools.grep_tool import GrepTool
from mcp.local_tools.quote_extract_tool import QuoteExtractTool
from mcp.local_tools.read_tool import ReadTool
from mcp.local_tools.report_template_tool import ReportTemplateTool
from mcp.local_tools.skill_executor_tool import SkillExecutorTool
from mcp.local_tools.skill_init_tool import SkillInitTool
from mcp.local_tools.source_compare_tool import SourceCompareTool
from mcp.local_tools.sub_agent_tool import SubAgentTool
from mcp.local_tools.thinking_tool import ThinkingTool
from mcp.local_tools.time_tool import TimeTool
from mcp.local_tools.web_fetch_tool import WebFetchTool
from mcp.local_tools.web_search_tool import WebSearchTool
from mcp.local_tools.write_file_tool import WriteFileTool

from .base import BaseLocalMCPServer


class FilesystemMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="filesystem",
        name="Filesystem Tools",
        description="Local filesystem and shell tools.",
        tools=["bash", "read", "write_file", "glob", "grep", "edit"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            BashTool(target.agent_root),
            ReadTool(target.agent_root),
            WriteFileTool(target.agent_root),
            GlobTool(target.agent_root),
            GrepTool(target.agent_root),
            EditTool(target.agent_root),
        ]


class SystemMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="system",
        name="System Tools",
        description="Local time, reminders, and user input tools.",
        tools=["time", "alarm", "ask_human"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            TimeTool(),
            AlarmTool(target._handle_system_message),
            AskHumanTool(target.ask_human_manager),
        ]


class ResearchMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="research",
        name="Research Tools",
        description="Local fetch, compare, citation, and report helpers.",
        tools=["web_fetch", "quote_extract", "source_compare", "report_template", "cite_manager"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            WebFetchTool(),
            QuoteExtractTool(),
            SourceCompareTool(),
            ReportTemplateTool(),
            CiteManagerTool(),
        ]


class BraveSearchMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="brave_search",
        name="Brave Search",
        description="Local Brave-backed web search tool.",
        requires_secrets=True,
        required_secrets=["BRAVE_API_KEY"],
        default_enabled=False,
        tools=["web_search"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [WebSearchTool()]


class SkillsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="skills",
        name="Skills Tools",
        description="Skill loading and skill package management.",
        tools=["skill", "skill_exec", "skill_init"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        skills_root = os.path.join(target.project_root, "skills")
        return [
            target.skill_tool,
            SkillExecutorTool(skills_root),
            SkillInitTool(skills_root),
        ]


class AgentMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="agent",
        name="Agent Helpers",
        description="Sub-agent orchestration and reasoning helpers.",
        tools=["sub_agent", "thinking"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            SubAgentTool(list(built_tools), target.skill_runtime),
            ThinkingTool(),
        ]
