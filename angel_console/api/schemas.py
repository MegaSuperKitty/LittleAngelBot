# -*- coding: utf-8 -*-
"""API schemas for angel console."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    request_id: str = ""
    user_id: str = "web:local"
    session_name: str = ""
    content: str = Field(..., min_length=1)
    continue_mode: str = "in_place"
    source: str = "web"
    inject_uploaded_files: bool = True


class CancelRequest(BaseModel):
    request_id: str


class HumanInputRequest(BaseModel):
    user_id: str
    content: str = Field(..., min_length=1)


class SessionNewRequest(BaseModel):
    user_id: str = "web:local"


class SessionSelectRequest(BaseModel):
    user_id: str
    session_name: str


class FileUploadMeta(BaseModel):
    user_id: str = "web:local"


class CronJobCreateRequest(BaseModel):
    cron_expr: str
    user_id: str = "web:local"
    session_name: str = ""
    prompt: str


class CronJobUpdateRequest(BaseModel):
    cron_expr: Optional[str] = None
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    prompt: Optional[str] = None
    enabled: Optional[bool] = None
    paused: Optional[bool] = None


class HeartbeatUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    interval_seconds: Optional[int] = None
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    prompt: Optional[str] = None


class ModelProfileUpsertRequest(BaseModel):
    profile_id: str
    provider: str
    base_url: str = ""
    model: str = ""
    api_key: str
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    clear_api_key: bool = False


class ModelProfileActivateRequest(BaseModel):
    profile_id: str


class ChannelUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    bot_prefix: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
