# -*- coding: utf-8 -*-
"""Cron routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import CronJobCreateRequest, CronJobUpdateRequest


router = APIRouter(prefix="/api/v1/cron", tags=["cron"])


def _engine(request: Request):
    engine = getattr(request.app.state, "cron_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="cron_not_ready")
    return engine


@router.get("/jobs")
def list_jobs(request: Request):
    engine = _engine(request)
    return {"jobs": engine.list_jobs()}


@router.post("/jobs")
def create_job(body: CronJobCreateRequest, request: Request):
    engine = _engine(request)
    try:
        job = engine.create_job(
            cron_expr=body.cron_expr,
            user_id=body.user_id,
            session_name=body.session_name,
            prompt=body.prompt,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"job": job}


@router.put("/jobs/{job_id}")
def update_job(job_id: str, body: CronJobUpdateRequest, request: Request):
    engine = _engine(request)
    patch = body.model_dump(exclude_none=True)
    try:
        job = engine.update_job(job_id, patch)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str, request: Request):
    engine = _engine(request)
    success = engine.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"success": True}


@router.post("/jobs/{job_id}/pause")
def pause_job(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.pause_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.post("/jobs/{job_id}/resume")
def resume_job(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.resume_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.post("/jobs/{job_id}/run")
def run_job(job_id: str, request: Request):
    engine = _engine(request)
    success = engine.run_now(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"success": True}
