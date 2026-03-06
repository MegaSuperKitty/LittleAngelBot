# -*- coding: utf-8 -*-
"""Synchronization helpers that apply MCP runtime state to host objects."""

from __future__ import annotations

from typing import Any

from mcp.runtime import MCPRuntime
from mcp.local_tools.skill_tool import sync_skill_runtime


def sync_mcp_runtime(target: Any, runtime: MCPRuntime = None):
    current_runtime = runtime or getattr(target, "mcp_runtime", None)
    if current_runtime is None:
        raise ValueError("sync_mcp_runtime requires an MCPRuntime.")
    snapshot = current_runtime.sync(target=target)
    setattr(target, "tools", list(snapshot.active_tools))
    base_prompt = str(getattr(target, "_base_system_prompt", "") or "")
    if any(getattr(tool, "name", "") == "skill" for tool in snapshot.active_tools) and hasattr(target, "skill_runtime"):
        sync_skill_runtime(target)
    else:
        setattr(target, "system_prompt", base_prompt)
    return snapshot
