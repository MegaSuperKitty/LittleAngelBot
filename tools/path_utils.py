# -*- coding: utf-8 -*-
"""Path utilities for sandboxed tool access."""

from __future__ import annotations

import os
from typing import Optional


def normalize_root(path: str) -> str:
    """Normalize root.
    
    Args:
        path (str): Filesystem path used by this operation.
    
    Returns:
        str: Result produced by this function.
    """
    root = os.path.abspath(path)
    return root


def is_within_base(path: str, base: str) -> bool:
    """Is within base.
    
    Args:
        path (str): Filesystem path used by this operation.
        base (str): Input value for base.
    
    Returns:
        bool: True when the condition is satisfied; otherwise False.
    """
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(base)]) == os.path.abspath(base)
    except ValueError:
        return False


def resolve_relative_path(base: str, rel: Optional[str]) -> str:
    """Resolve relative path.
    
    Args:
        base (str): Input value for base.
        rel (Optional[str]): Input value for rel.
    
    Returns:
        str: Result produced by this function.
    
    Raises:
        ValueError: Raised when an execution error occurs.
    """
    if not rel:
        return os.path.abspath(base)
    if os.path.isabs(rel):
        raise ValueError("Absolute paths are not allowed.")
    candidate = os.path.abspath(os.path.join(base, rel))
    if not is_within_base(candidate, base):
        raise ValueError("Path escapes base directory.")
    return candidate


def require_existing_dir(path: str) -> None:
    """Require existing dir.
    
    Args:
        path (str): Filesystem path used by this operation.
    
    Returns:
        None: This method does not return a value.
    
    Raises:
        ValueError: Raised when an execution error occurs.
    """
    if not os.path.isdir(path):
        raise ValueError("Directory does not exist.")
