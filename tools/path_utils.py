# -*- coding: utf-8 -*-
"""Path utilities for sandboxed tool access."""

from __future__ import annotations

import os
from typing import Optional


def normalize_root(path: str) -> str:
    root = os.path.abspath(path)
    return root


def is_within_base(path: str, base: str) -> bool:
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(base)]) == os.path.abspath(base)
    except ValueError:
        return False


def resolve_relative_path(base: str, rel: Optional[str]) -> str:
    if not rel:
        return os.path.abspath(base)
    if os.path.isabs(rel):
        raise ValueError("Absolute paths are not allowed.")
    candidate = os.path.abspath(os.path.join(base, rel))
    if not is_within_base(candidate, base):
        raise ValueError("Path escapes base directory.")
    return candidate


def require_existing_dir(path: str) -> None:
    if not os.path.isdir(path):
        raise ValueError("Directory does not exist.")
