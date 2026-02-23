# -*- coding: utf-8 -*-
"""Lightweight cron scheduler for LittleAngel console."""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Any, Dict, List, Optional
import uuid

from croniter import croniter

from .store import JsonStore, now_iso


@dataclass
class JobRunResult:
    status: str
    result: str


class CronEngine:
    """Persisted cron job manager with background loop."""

    def __init__(self, runtime, data_path: str):
        self.runtime = runtime
        self.store = JsonStore(data_path)
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._load()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="angel-cron-loop")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = [dict(job) for job in self._jobs.values()]
        rows.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        return rows

    def create_job(self, cron_expr: str, user_id: str, session_name: str, prompt: str) -> Dict[str, Any]:
        self._validate_cron(cron_expr)
        job_id = str(uuid.uuid4())
        now_ts = time.time()
        job = {
            "id": job_id,
            "cron_expr": cron_expr.strip(),
            "user_id": (user_id or "web:local").strip(),
            "session_name": (session_name or "").strip(),
            "prompt": (prompt or "").strip(),
            "enabled": True,
            "paused": False,
            "running": False,
            "next_run_ts": self._next_run_ts(cron_expr, now_ts),
            "last_run_at": "",
            "last_status": "never",
            "last_result": "",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        with self._lock:
            self._jobs[job_id] = job
            self._save_locked()
        return dict(job)

    def update_job(self, job_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if "cron_expr" in patch:
                expr = str(patch["cron_expr"] or "").strip()
                self._validate_cron(expr)
                job["cron_expr"] = expr
                job["next_run_ts"] = self._next_run_ts(expr, time.time())
            for key in ["user_id", "session_name", "prompt"]:
                if key in patch:
                    job[key] = str(patch[key] or "").strip()
            if "enabled" in patch:
                job["enabled"] = bool(patch["enabled"])
            if "paused" in patch:
                job["paused"] = bool(patch["paused"])
            job["updated_at"] = now_iso()
            self._save_locked()
            return dict(job)

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            existed = job_id in self._jobs
            if existed:
                self._jobs.pop(job_id, None)
                self._save_locked()
            return existed

    def pause_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.update_job(job_id, {"paused": True})

    def resume_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        updated = self.update_job(job_id, {"paused": False, "enabled": True})
        return updated

    def run_now(self, job_id: str) -> bool:
        with self._lock:
            if job_id not in self._jobs:
                return False
        threading.Thread(target=self._execute_job, args=(job_id, False), daemon=True).start()
        return True

    def _loop(self) -> None:
        while self._running:
            due_ids: List[str] = []
            now_ts = time.time()
            with self._lock:
                for job_id, job in self._jobs.items():
                    if not job.get("enabled", True):
                        continue
                    if job.get("paused", False):
                        continue
                    if job.get("running", False):
                        continue
                    next_ts = float(job.get("next_run_ts", 0) or 0)
                    if next_ts <= now_ts:
                        due_ids.append(job_id)
            for job_id in due_ids:
                threading.Thread(target=self._execute_job, args=(job_id, True), daemon=True).start()
            time.sleep(1.0)

    def _execute_job(self, job_id: str, schedule_next: bool) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.get("running"):
                return
            job["running"] = True
            job["updated_at"] = now_iso()
            self._save_locked()
            snap = dict(job)

        status = "completed"
        result = ""
        try:
            result = self.runtime.run_background_prompt(
                user_id=snap["user_id"],
                session_name=snap.get("session_name", ""),
                content=snap.get("prompt", ""),
                source="cron",
            )
        except Exception as exc:
            status = "failed"
            result = f"{exc}"

        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["running"] = False
            job["last_run_at"] = now_iso()
            job["last_status"] = status
            job["last_result"] = str(result or "")[:2000]
            if schedule_next:
                job["next_run_ts"] = self._next_run_ts(job["cron_expr"], time.time())
            else:
                # Keep schedule moving forward even for manual runs.
                job["next_run_ts"] = self._next_run_ts(job["cron_expr"], time.time())
            job["updated_at"] = now_iso()
            self._save_locked()

    def _validate_cron(self, cron_expr: str) -> None:
        text = (cron_expr or "").strip()
        if not text:
            raise ValueError("cron_expr is required")
        croniter(text, time.time())

    def _next_run_ts(self, cron_expr: str, from_ts: float) -> float:
        itr = croniter(cron_expr, from_ts)
        return float(itr.get_next(float))

    def _load(self) -> None:
        raw = self.store.read({"jobs": []})
        jobs = raw.get("jobs", []) if isinstance(raw, dict) else []
        if not isinstance(jobs, list):
            jobs = []
        with self._lock:
            self._jobs = {}
            for row in jobs:
                if not isinstance(row, dict):
                    continue
                job_id = str(row.get("id") or "").strip()
                if not job_id:
                    continue
                row["running"] = False
                self._jobs[job_id] = row

    def _save_locked(self) -> None:
        payload = {"jobs": list(self._jobs.values())}
        self.store.write(payload)
