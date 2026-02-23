# -*- coding: utf-8 -*-
"""Channel configuration routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import ChannelUpdateRequest


router = APIRouter(prefix="/api/v1/channels", tags=["channels"])


def _manager(request: Request):
    manager = getattr(request.app.state, "channel_manager", None)
    if manager is None:
        raise HTTPException(status_code=503, detail="channel_manager_not_ready")
    return manager


@router.get("")
def get_channels(request: Request):
    return _manager(request).get_state()


@router.put("/{channel_name}")
def update_channel(channel_name: str, body: ChannelUpdateRequest, request: Request):
    manager = _manager(request)
    try:
        return manager.update_channel(
            channel_name=channel_name,
            enabled=body.enabled,
            bot_prefix=body.bot_prefix,
            settings=body.settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
