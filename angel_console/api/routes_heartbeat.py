# -*- coding: utf-8 -*-
"""Heartbeat routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import HeartbeatUpdateRequest


router = APIRouter(prefix="/api/v1/heartbeat", tags=["heartbeat"])


def _engine(request: Request):
    engine = getattr(request.app.state, "heartbeat_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="heartbeat_not_ready")
    return engine


@router.get("")
def get_heartbeat(request: Request):
    engine = _engine(request)
    return {"heartbeat": engine.get_spec()}


@router.put("")
def update_heartbeat(body: HeartbeatUpdateRequest, request: Request):
    engine = _engine(request)
    patch = body.model_dump(exclude_none=True)
    spec = engine.update_spec(patch)
    return {"heartbeat": spec}


@router.post("/run")
def run_heartbeat(request: Request):
    engine = _engine(request)
    return engine.run_now()
