# -*- coding: utf-8 -*-
"""Skills routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


def _catalog(request: Request):
    catalog = getattr(request.app.state, "skills_catalog", None)
    if catalog is None:
        raise HTTPException(status_code=503, detail="skills_not_ready")
    return catalog


@router.get("")
def list_skills(request: Request):
    catalog = _catalog(request)
    return {"success": True, "skills": catalog.list_skills()}
