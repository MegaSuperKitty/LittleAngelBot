# -*- coding: utf-8 -*-
"""Shared path and config helpers for channel entrypoints."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HISTORY_DIR = (PROJECT_ROOT / "chat_history").resolve()
LOCAL_SECRETS_PATH = (PROJECT_ROOT / "local_secrets.yaml").resolve()
CHANNEL_CONFIG_PATH = (PROJECT_ROOT / "angel_console" / "data" / "channels.json").resolve()


def resolve_agent_root() -> Path:
    env_root = os.getenv("WE_CLAW_AGENT_WORKSPACE", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    return (PROJECT_ROOT / "agent_workspace").resolve()


AGENT_ROOT = resolve_agent_root()
AGENT_ROOT.mkdir(parents=True, exist_ok=True)


def load_local_secrets(path: Path = LOCAL_SECRETS_PATH) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_channel_settings(channel_name: str, path: Path = CHANNEL_CONFIG_PATH) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    channels = payload.get("channels", payload)
    if not isinstance(channels, dict):
        return {}
    row = channels.get(channel_name, {})
    return row if isinstance(row, dict) else {}
