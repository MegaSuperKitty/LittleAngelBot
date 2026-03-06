# -*- coding: utf-8 -*-
"""Runtime manager for enabled MCP clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Tuple
import os

from mcp.mcp_server import get_server
from mcp.remote_client import build_remote_tools
from mcp.schema import MCPClientConfig, MCPToolBinding
from mcp.secrets import resolve_secret_refs


@dataclass
class _ManagedClient:
    config: MCPClientConfig
    tools: List[object]


class MCPClientManager:
    """Manage active local/remote MCP client instances."""

    def __init__(self):
        self._clients: Dict[str, _ManagedClient] = {}

    def sync_active(
        self,
        active_configs: List[MCPClientConfig],
        secrets: Mapping[str, str],
        target,
    ) -> Tuple[List[object], List[MCPToolBinding], Dict[str, List[Dict[str, Any]]], Dict[str, str]]:
        self._clients = {}
        built_tools: List[object] = []
        bindings: List[MCPToolBinding] = []
        available_tools_by_client: Dict[str, List[Dict[str, Any]]] = {}
        errors: Dict[str, str] = {}

        for config in sorted(active_configs, key=self._build_sort_key):
            try:
                tools, available_tools = self._build_client_tools(config, secrets, target, built_tools)
            except Exception as exc:
                tools = []
                available_tools = []
                errors[config.client_id] = str(exc)
            filtered_tools = self._filter_tools(tools, config.enabled_tools)
            available_tools_by_client[config.client_id] = list(available_tools)
            self._clients[config.client_id] = _ManagedClient(config=config, tools=filtered_tools)
            for tool in filtered_tools:
                built_tools.append(tool)
                bindings.append(
                    MCPToolBinding(
                        client_id=config.client_id,
                        server_id=config.server_id or config.client_id,
                        mode=config.mode,
                        tool_name=getattr(tool, "name", ""),
                        description=getattr(tool, "description", ""),
                    )
                )
        return built_tools, bindings, available_tools_by_client, errors

    def client_rows(self) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for managed in self._clients.values():
            rows.append(
                {
                    "client_id": managed.config.client_id,
                    "name": managed.config.name,
                    "enabled": managed.config.enabled,
                    "mode": managed.config.mode,
                    "tool_count": len(managed.tools),
                }
            )
        return rows

    def _build_client_tools(
        self,
        config: MCPClientConfig,
        secrets: Mapping[str, str],
        target,
        built_tools: List[object],
    ) -> Tuple[List[object], List[Dict[str, Any]]]:
        resolved = resolve_secret_refs(config.secret_refs, secrets)
        if config.mode == "local":
            self._apply_env(config.env, resolved)
            server = get_server(config.server_id)
            if server is None:
                return [], []
            tools = server.build_tools(target, built_tools)
            return tools, [self._tool_descriptor(tool) for tool in tools]
        if config.mode == "remote":
            return build_remote_tools(config, resolved)
        return [], []

    def _build_sort_key(self, config: MCPClientConfig):
        priority = 10
        if config.mode == "remote":
            priority = 20
        if (config.server_id or config.client_id) == "agent":
            priority = 100
        return (priority, config.client_id)

    def _apply_env(self, env_map: Mapping[str, str], resolved: Mapping[str, str]) -> None:
        merged: Dict[str, str] = {}
        merged.update({str(k): str(v) for k, v in (env_map or {}).items() if str(v).strip()})
        for key, value in (resolved or {}).items():
            env_key = str(key or "").strip()
            if env_key and str(value).strip():
                merged[env_key] = str(value)
        for key, value in merged.items():
            os.environ[key] = value

    def _filter_tools(self, tools: List[object], enabled_tools: List[str]) -> List[object]:
        selected = {str(name or "").strip() for name in (enabled_tools or []) if str(name or "").strip()}
        if not selected:
            return list(tools)
        return [tool for tool in tools if str(getattr(tool, "name", "") or "").strip() in selected]

    def _tool_descriptor(self, tool: object) -> Dict[str, Any]:
        return {
            "name": str(getattr(tool, "name", "") or "").strip(),
            "description": str(getattr(tool, "description", "") or "").strip(),
            "input_schema": dict(getattr(tool, "parameters", {}) or {}),
        }
