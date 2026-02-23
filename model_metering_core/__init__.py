# -*- coding: utf-8 -*-
"""Public entrypoints for model metering core."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .engine import ModelMeteringEngine


_DEFAULT_ENGINE: Optional[ModelMeteringEngine] = None


def default_log_dir() -> str:
    env = str(os.getenv("MODEL_CALL_LOG_DIR", "")).strip()
    if env:
        return str(Path(env).resolve())
    root = Path(__file__).resolve().parent.parent
    return str((root / "model_call_logs").resolve())


def get_default_engine(log_dir: str = "") -> ModelMeteringEngine:
    global _DEFAULT_ENGINE
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = ModelMeteringEngine(log_dir or default_log_dir())
    return _DEFAULT_ENGINE


__all__ = [
    "ModelMeteringEngine",
    "get_default_engine",
    "default_log_dir",
]
