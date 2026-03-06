# -*- coding: utf-8 -*-
"""High-level MCP runtime: discovery, configuration, and active tool state."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from mcp.discovery import (
    default_client_configs,
    delete_client_config,
    discover_local_servers,
    ensure_default_client_configs,
    load_client_configs,
    save_client_config,
)
from mcp.manager import MCPClientManager
from mcp.schema import MCPClientConfig, MCPRuntimeSnapshot
from mcp.secrets import load_mcp_secrets, mask_secret, resolve_secret_value, save_mcp_secrets, stable_secret_ref


class MCPRuntime:
    """Own discovery/configuration state for MCP-backed tools."""

    def __init__(
        self,
        project_root: str,
        client_dir: Optional[str] = None,
        secrets_path: Optional[str] = None,
    ):
        self.project_root = str(Path(project_root).resolve())
        self.client_dir = str(Path(client_dir or (Path(self.project_root) / "mcp" / "mcp_client")).resolve())
        self.secrets_path = str(Path(secrets_path or (Path(self.project_root) / "local_mcp_secrets.yaml")).resolve())
        self.manager = MCPClientManager()
        self._snapshot = MCPRuntimeSnapshot()
        ensure_default_client_configs(self.client_dir)

    def sync(self, target=None) -> MCPRuntimeSnapshot:
        discovered = discover_local_servers()
        configured = load_client_configs(self.client_dir)
        secrets = load_mcp_secrets(self.secrets_path)
        active = [config for config in configured if config.enabled]
        active_tools, bindings, available_by_client, errors = self.manager.sync_active(active, secrets, target)
        self._cache_remote_tool_catalog(configured, available_by_client)
        configured_rows = self._build_configured_rows(
            configured=configured,
            discovered=discovered,
            secrets=secrets,
            available_by_client=available_by_client,
            bindings=bindings,
            errors=errors,
        )
        self._snapshot = MCPRuntimeSnapshot(
            discovered=list(discovered),
            configured=list(configured_rows),
            active_clients=list(active),
            active_tools=list(active_tools),
            tool_bindings=list(bindings),
        )
        return self._snapshot

    def snapshot(self) -> MCPRuntimeSnapshot:
        return self._snapshot

    def discover_rows(self) -> List[Dict[str, object]]:
        return self._snapshot.discovered_rows() if self._snapshot.discovered else [item.to_dict() for item in discover_local_servers()]

    def configured_rows(self) -> List[Dict[str, object]]:
        if self._snapshot.configured:
            return self._snapshot.configured_rows()
        rows: List[Dict[str, object]] = []
        secrets = load_mcp_secrets(self.secrets_path)
        discovered_by_id = {item.server_id: item for item in discover_local_servers()}
        for config in load_client_configs(self.client_dir):
            rows.append(
                self._build_client_row(
                    config=config,
                    discovered_by_id=discovered_by_id,
                    secrets=secrets,
                    available_tools=None,
                    active_tool_names=[],
                    runtime_error="",
                )
            )
        return rows

    def upsert_client(
        self,
        config: MCPClientConfig,
        target=None,
        *,
        original_client_id: str = "",
        secret_values: Optional[Mapping[str, object]] = None,
    ) -> MCPRuntimeSnapshot:
        normalized = config.normalized()
        current_configs = {item.client_id: item for item in load_client_configs(self.client_dir)}
        existing = current_configs.get(str(original_client_id or normalized.client_id).strip())
        if original_client_id and existing is None:
            raise ValueError(f"MCP client not found: {original_client_id}")
        if original_client_id and normalized.client_id != str(original_client_id).strip():
            raise ValueError("client_id cannot be changed after creation.")
        if existing is not None:
            normalized = self._merge_client(existing, normalized)
        self._apply_secret_updates(normalized, existing, secret_values)
        save_client_config(self.client_dir, normalized.normalized())
        if target is None:
            return self.sync()
        from mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def toggle_client(self, client_id: str, enabled: bool, target=None) -> MCPRuntimeSnapshot:
        configs = {config.client_id: config for config in load_client_configs(self.client_dir)}
        current = configs.get(client_id)
        if current is None:
            raise ValueError(f"MCP client not found: {client_id}")
        current.enabled = bool(enabled)
        save_client_config(self.client_dir, current.normalized())
        if target is None:
            return self.sync()
        from mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def delete_client(self, client_id: str, target=None) -> MCPRuntimeSnapshot:
        delete_client_config(self.client_dir, client_id)
        if target is None:
            return self.sync()
        from mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def default_rows(self) -> List[Dict[str, object]]:
        return [config.to_dict() for config in default_client_configs()]

    def _merge_client(self, existing: MCPClientConfig, incoming: MCPClientConfig) -> MCPClientConfig:
        incoming.secret_refs = dict(existing.secret_refs)
        if not incoming.server_id and existing.server_id:
            incoming.server_id = existing.server_id
        if not incoming.endpoint and existing.endpoint:
            incoming.endpoint = existing.endpoint
        if not incoming.headers and existing.headers:
            incoming.headers = dict(existing.headers)
        if not incoming.env and existing.env:
            incoming.env = dict(existing.env)
        metadata = dict(existing.metadata or {})
        metadata.update(dict(incoming.metadata or {}))
        incoming.metadata = metadata
        return incoming

    def _apply_secret_updates(
        self,
        config: MCPClientConfig,
        existing: Optional[MCPClientConfig],
        secret_values: Optional[Mapping[str, object]],
    ) -> None:
        refs = dict(config.secret_refs or {})
        if existing is not None:
            refs.update({str(k): str(v) for k, v in (existing.secret_refs or {}).items() if str(k).strip() and str(v).strip()})

        for slot_name in self._required_secret_slots(config):
            refs.setdefault(slot_name, stable_secret_ref(config.client_id, slot_name))

        updates: Dict[str, str] = {}
        for slot_name, raw_value in (secret_values or {}).items():
            slot = str(slot_name or "").strip()
            value = str(raw_value or "").strip()
            if not slot or not value:
                continue
            refs.setdefault(slot, stable_secret_ref(config.client_id, slot))
            secret_ref = str(refs.get(slot) or "").strip()
            if secret_ref:
                updates[secret_ref] = value

        if updates:
            save_mcp_secrets(self.secrets_path, updates)
        config.secret_refs = refs

    def _required_secret_slots(self, config: MCPClientConfig) -> List[str]:
        if config.mode == "local":
            discovered_by_id = {item.server_id: item for item in discover_local_servers()}
            server = discovered_by_id.get(config.server_id)
            if server and server.requires_secrets:
                return [str(item).strip() for item in (server.required_secrets or []) if str(item).strip()]
            return []
        slots = [str(key).strip() for key in (config.secret_refs or {}).keys() if str(key).strip()]
        if slots:
            return slots
        return ["api_key"]

    def _cache_remote_tool_catalog(
        self,
        configured: List[MCPClientConfig],
        available_by_client: Mapping[str, List[Dict[str, Any]]],
    ) -> None:
        for config in configured:
            if config.mode != "remote":
                continue
            catalog = [dict(item) for item in (available_by_client.get(config.client_id) or []) if isinstance(item, dict)]
            if not catalog:
                continue
            cached = config.metadata.get("cached_tools")
            if cached == catalog:
                continue
            config.metadata["cached_tools"] = catalog
            save_client_config(self.client_dir, config.normalized())

    def _build_configured_rows(
        self,
        *,
        configured: List[MCPClientConfig],
        discovered: List[Any],
        secrets: Mapping[str, str],
        available_by_client: Mapping[str, List[Dict[str, Any]]],
        bindings,
        errors: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        discovered_by_id = {
            str(item.server_id): item
            for item in discovered
            if hasattr(item, "server_id") and str(getattr(item, "server_id", "")).strip()
        }
        active_by_client: Dict[str, List[str]] = {}
        for binding in bindings:
            active_by_client.setdefault(str(binding.client_id), []).append(str(binding.tool_name))

        rows: List[Dict[str, Any]] = []
        for config in configured:
            available_tools = available_by_client.get(config.client_id)
            rows.append(
                self._build_client_row(
                    config=config,
                    discovered_by_id=discovered_by_id,
                    secrets=secrets,
                    available_tools=available_tools,
                    active_tool_names=active_by_client.get(config.client_id, []),
                    runtime_error=str(errors.get(config.client_id, "") or ""),
                )
            )
        return rows

    def _build_client_row(
        self,
        *,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        secrets: Mapping[str, str],
        available_tools: Optional[List[Dict[str, Any]]],
        active_tool_names: List[str],
        runtime_error: str,
    ) -> Dict[str, Any]:
        tools = self._available_tools_for_client(config, discovered_by_id, available_tools)
        selected = {str(name).strip() for name in (config.enabled_tools or []) if str(name).strip()}
        tool_rows: List[Dict[str, Any]] = []
        for item in tools:
            tool_name = str(item.get("name") or "").strip()
            if not tool_name:
                continue
            tool_rows.append(
                {
                    "name": tool_name,
                    "description": str(item.get("description") or "").strip(),
                    "selected": (tool_name in selected) if selected else True,
                }
            )
        secret_slots = self._secret_slots_for_client(config, discovered_by_id, secrets)
        row = config.to_api_dict(
            available_tools=tool_rows,
            active_tool_names=active_tool_names,
            secret_slots=secret_slots,
            runtime_error=runtime_error,
        )
        return row

    def _available_tools_for_client(
        self,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        available_tools: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        if available_tools:
            return [dict(item) for item in available_tools if isinstance(item, dict)]
        if config.mode == "local":
            server = discovered_by_id.get(config.server_id)
            if server is None:
                return []
            return [{"name": str(name), "description": ""} for name in (server.tools or []) if str(name).strip()]
        cached = config.metadata.get("cached_tools")
        if isinstance(cached, list):
            return [dict(item) for item in cached if isinstance(item, dict)]
        return []

    def _secret_slots_for_client(
        self,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        secrets: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        slot_names = self._required_secret_slots(config)
        if not slot_names and config.secret_refs:
            slot_names = [str(key).strip() for key in config.secret_refs.keys() if str(key).strip()]
        rows: List[Dict[str, Any]] = []
        for slot_name in slot_names:
            secret_ref = str((config.secret_refs or {}).get(slot_name) or "").strip()
            value = resolve_secret_value(slot_name, secret_ref, secrets)
            rows.append(
                {
                    "slot_name": slot_name,
                    "secret_ref": secret_ref,
                    "has_value": bool(value),
                    "masked_value": mask_secret(value),
                }
            )
        if config.mode == "local":
            server = discovered_by_id.get(config.server_id)
            if server is not None and not server.requires_secrets:
                for row in rows:
                    row["note"] = ""
        return rows
