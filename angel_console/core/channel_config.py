# -*- coding: utf-8 -*-
"""Channel configuration manager for console channel cards."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

import yaml


def _channel_definitions() -> Dict[str, Dict[str, Any]]:
    return {
        "web": {
            "display_name": "Browser",
            "description": "Web Console (local)",
            "tag": "builtin",
            "defaults": {
                "enabled": True,
                "bot_prefix": "",
                "settings": {
                    "base_url": "http://127.0.0.1:7788",
                    "bind_host": "127.0.0.1",
                    "port": "7788",
                },
            },
            "fields": [
                {
                    "key": "base_url",
                    "type": "text",
                    "required": False,
                    "secret": False,
                    "placeholder": "http://127.0.0.1:7788",
                    "env_keys": [],
                },
                {
                    "key": "bind_host",
                    "type": "text",
                    "required": False,
                    "secret": False,
                    "placeholder": "127.0.0.1",
                    "env_keys": [],
                },
                {
                    "key": "port",
                    "type": "number",
                    "required": False,
                    "secret": False,
                    "placeholder": "7788",
                    "env_keys": [],
                },
            ],
            "launch_hint": "uvicorn angel_console.app:app --host 127.0.0.1 --port 7788",
        },
        "cli": {
            "display_name": "CLI",
            "description": "Local command line",
            "tag": "builtin",
            "defaults": {
                "enabled": True,
                "bot_prefix": "",
                "settings": {
                    "command": ".\\.venv\\Scripts\\python.exe entry_cli.py",
                },
            },
            "fields": [
                {
                    "key": "command",
                    "type": "text",
                    "required": False,
                    "secret": False,
                    "placeholder": ".\\.venv\\Scripts\\python.exe entry_cli.py",
                    "env_keys": [],
                }
            ],
            "launch_hint": ".\\.venv\\Scripts\\python.exe entry_cli.py",
        },
        "qq": {
            "display_name": "QQ",
            "description": "QQ channel (botpy)",
            "tag": "external",
            "defaults": {
                "enabled": False,
                "bot_prefix": "",
                "settings": {
                    "app_id": "",
                    "client_secret": "",
                },
            },
            "fields": [
                {
                    "key": "app_id",
                    "type": "text",
                    "required": True,
                    "secret": False,
                    "placeholder": "Bot App ID",
                    "env_keys": ["BOTPY_APPID"],
                },
                {
                    "key": "client_secret",
                    "type": "password",
                    "required": True,
                    "secret": True,
                    "placeholder": "Bot Secret",
                    "env_keys": ["BOTPY_SECRET"],
                },
            ],
            "launch_hint": ".\\.venv\\Scripts\\python.exe entry_qq.py",
        },
        "discord": {
            "display_name": "Discord",
            "description": "Discord channel",
            "tag": "external",
            "defaults": {
                "enabled": False,
                "bot_prefix": "",
                "settings": {
                    "bot_token": "",
                    "http_proxy": "",
                    "http_proxy_auth": "",
                    "guild_id": "",
                },
            },
            "fields": [
                {
                    "key": "bot_token",
                    "type": "password",
                    "required": True,
                    "secret": True,
                    "placeholder": "Discord Bot Token",
                    "env_keys": ["DISCORD_BOT_TOKEN"],
                },
                {
                    "key": "http_proxy",
                    "type": "text",
                    "required": False,
                    "secret": False,
                    "placeholder": "http://127.0.0.1:7890",
                    "env_keys": ["DISCORD_HTTP_PROXY"],
                },
                {
                    "key": "http_proxy_auth",
                    "type": "password",
                    "required": False,
                    "secret": True,
                    "placeholder": "username:password",
                    "env_keys": ["DISCORD_HTTP_PROXY_AUTH"],
                },
                {
                    "key": "guild_id",
                    "type": "text",
                    "required": False,
                    "secret": False,
                    "placeholder": "Guild ID (optional)",
                    "env_keys": ["DISCORD_GUILD_ID"],
                },
            ],
            "launch_hint": ".\\.venv\\Scripts\\python.exe entry_discord.py",
        },
    }


def _load_channel_settings(data_path: Path) -> Dict[str, Any]:
    if not data_path.is_file():
        return {}
    try:
        payload = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_local_secrets(path: Path) -> Dict[str, str]:
    if not path.is_file():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    out: Dict[str, str] = {}
    for key, value in payload.items():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            out[str(key)] = text
    return out


class ChannelConfigManager:
    """Read/write channel card settings."""

    def __init__(self, data_path: str, secrets_path: str):
        self.data_path = Path(data_path).resolve()
        self.secrets_path = Path(secrets_path).resolve()
        self._defs = _channel_definitions()
        self._lock = threading.Lock()

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            current = self._read_locked()
            channels = [self._build_channel_state(name, current.get(name, {})) for name in self._defs.keys()]
            return {"channels": channels}

    def update_channel(
        self,
        channel_name: str,
        enabled: Optional[bool] = None,
        bot_prefix: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        name = (channel_name or "").strip().lower()
        if name not in self._defs:
            raise ValueError("channel not found")

        with self._lock:
            raw = self._read_locked()
            row = raw.get(name, {}) if isinstance(raw.get(name), dict) else {}
            merged = self._merge_with_defaults(name, row)

            if enabled is not None:
                merged["enabled"] = bool(enabled)
                merged["manual_enabled"] = True
            if bot_prefix is not None:
                merged["bot_prefix"] = str(bot_prefix or "").strip()

            incoming = settings if isinstance(settings, dict) else {}
            field_map = {f["key"]: f for f in self._defs[name]["fields"]}
            for key, value in incoming.items():
                if key not in field_map:
                    continue
                field = field_map[key]
                text = str(value or "").strip()
                if field.get("secret"):
                    # Secret fields: blank keeps existing/fallback.
                    if text:
                        merged["settings"][key] = text
                else:
                    merged["settings"][key] = text

            effective = self._merge_with_fallback(name, merged)
            missing = self._missing_required(name, effective)
            effective_enabled = self._resolve_enabled(name, effective)
            if effective_enabled and missing:
                raise ValueError(f"missing required settings: {', '.join(missing)}")

            raw[name] = {
                "enabled": bool(merged.get("enabled", False)),
                "manual_enabled": bool(merged.get("manual_enabled", False)),
                "bot_prefix": str(merged.get("bot_prefix", "") or "").strip(),
                "settings": merged.get("settings", {}),
            }
            self._write_locked(raw)

            channels = [self._build_channel_state(ch, raw.get(ch, {})) for ch in self._defs.keys()]
            return {"channels": channels}

    # ---- internal ----

    def _read_locked(self) -> Dict[str, Any]:
        payload = _load_channel_settings(self.data_path)
        node = payload.get("channels", payload)
        if isinstance(node, dict):
            return node
        return {}

    def _write_locked(self, channels: Dict[str, Any]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"channels": channels}
        self.data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _merge_with_defaults(self, channel_name: str, row: Dict[str, Any]) -> Dict[str, Any]:
        spec = self._defs[channel_name]
        defaults = deepcopy(spec["defaults"])
        merged: Dict[str, Any] = {
            "enabled": bool(row.get("enabled", defaults["enabled"])),
            "manual_enabled": bool(row.get("manual_enabled", False)),
            "bot_prefix": str(row.get("bot_prefix", defaults["bot_prefix"]) or "").strip(),
            "settings": {},
        }
        source_settings = row.get("settings", {})
        source_settings = source_settings if isinstance(source_settings, dict) else {}
        for field in spec["fields"]:
            key = field["key"]
            default_value = str(defaults["settings"].get(key, "") or "")
            merged["settings"][key] = str(source_settings.get(key, default_value) or "").strip()
        return merged

    def _merge_with_fallback(self, channel_name: str, merged: Dict[str, Any]) -> Dict[str, Any]:
        out = deepcopy(merged)
        local_secrets = _load_local_secrets(self.secrets_path)
        for field in self._defs[channel_name]["fields"]:
            key = field["key"]
            current = str(out["settings"].get(key, "") or "").strip()
            if current:
                continue
            env_keys = field.get("env_keys", []) or []
            fallback = ""
            for env_key in env_keys:
                v = str(os.getenv(env_key, "") or "").strip()
                if v:
                    fallback = v
                    break
                s = str(local_secrets.get(env_key, "") or "").strip()
                if s:
                    fallback = s
                    break
            if fallback:
                out["settings"][key] = fallback
        return out

    def _missing_required(self, channel_name: str, row: Dict[str, Any]) -> List[str]:
        missing: List[str] = []
        settings = row.get("settings", {})
        settings = settings if isinstance(settings, dict) else {}
        for field in self._defs[channel_name]["fields"]:
            if not field.get("required"):
                continue
            key = field["key"]
            if not str(settings.get(key, "") or "").strip():
                missing.append(key)
        return missing

    def _resolve_enabled(self, channel_name: str, row: Dict[str, Any]) -> bool:
        manual_enabled = bool(row.get("manual_enabled", False))
        if manual_enabled:
            return bool(row.get("enabled", False))
        if channel_name in {"web", "cli"}:
            return True
        return len(self._missing_required(channel_name, row)) == 0

    def _build_channel_state(self, channel_name: str, row: Dict[str, Any]) -> Dict[str, Any]:
        spec = self._defs[channel_name]
        merged = self._merge_with_defaults(channel_name, row if isinstance(row, dict) else {})
        effective = self._merge_with_fallback(channel_name, merged)
        missing_required = self._missing_required(channel_name, effective)
        enabled = self._resolve_enabled(channel_name, effective)
        ready = (not enabled) or (len(missing_required) == 0)

        field_rows: List[Dict[str, Any]] = []
        for field in spec["fields"]:
            key = field["key"]
            value = str(effective["settings"].get(key, "") or "")
            secret = bool(field.get("secret"))
            field_rows.append(
                {
                    "key": key,
                    "type": field.get("type", "text"),
                    "required": bool(field.get("required", False)),
                    "secret": secret,
                    "placeholder": field.get("placeholder", ""),
                    "value": "" if secret else value,
                    "has_value": bool(value),
                }
            )

        return {
            "name": channel_name,
            "display_name": spec["display_name"],
            "description": spec["description"],
            "tag": spec["tag"],
            "enabled": enabled,
            "ready": ready,
            "missing_required": missing_required,
            "bot_prefix": effective["bot_prefix"],
            "launch_hint": spec.get("launch_hint", ""),
            "fields": field_rows,
        }
