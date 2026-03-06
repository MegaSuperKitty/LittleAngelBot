# -*- coding: utf-8 -*-
"""LittleAngel Console application entry."""

from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Ensure project root imports work when launching from angel_console/.
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from angel_console.api.routes_chat import router as chat_router
from angel_console.api.routes_billing import router as billing_router
from angel_console.api.routes_channels import router as channels_router
from angel_console.api.routes_cron import router as cron_router
from angel_console.api.routes_files import router as files_router
from angel_console.api.routes_heartbeat import router as heartbeat_router
from angel_console.api.routes_mcp import router as mcp_router
from angel_console.api.routes_models import router as models_router
from angel_console.api.routes_search import router as search_router
from angel_console.api.routes_sessions import router as sessions_router
from angel_console.api.routes_speech import router as speech_router
from angel_console.api.routes_skills import router as skills_router
from angel_console.core.bot_runtime import BotRuntime
from angel_console.core.channel_config_store import ChannelConfigStore
from angel_console.core.channel_runtime import ChannelRuntimeManager
from angel_console.core.channel_service import ChannelService
from angel_console.core.channel_specs import default_channel_specs
from angel_console.core.model_config import ModelConfigManager
from angel_console.core.speech_transcriber import LocalSpeechTranscriber
from angel_console.core.skills_catalog import SkillsCatalog
from angel_console.sched.cron_engine import CronEngine
from angel_console.sched.heartbeat_engine import HeartbeatEngine
from model_metering_core import get_default_engine
from retrieval_core.engine import RetrievalEngine


LOCAL_SECRETS_PATH = PROJECT_ROOT / "local_secrets.yaml"


def _load_local_secrets(path: Path) -> Dict[str, str]:
    if not path.is_file():
        return {}
    try:
        import yaml

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        out: Dict[str, str] = {}
        for key, value in data.items():
            if value is None:
                continue
            text = str(value).strip()
            if text:
                out[str(key)] = text
        return out
    except Exception:
        return {}


def _apply_local_secrets_to_env() -> None:
    secrets = _load_local_secrets(LOCAL_SECRETS_PATH)
    # Keep behavior aligned with CLI/QQ entries: env wins, local file is fallback.
    keys = [
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_MODEL",
        "LLM_PROVIDER",
        "LLM_PROFILE_ID",
        "BOTPY_APPID",
        "BOTPY_SECRET",
        "DISCORD_BOT_TOKEN",
        "DISCORD_APP_ID",
        "DISCORD_GUILD_ID",
        "DISCORD_HTTP_PROXY",
        "DISCORD_HTTP_PROXY_AUTH",
        "LLM_MAX_TOKENS",
        "LLM_TIMEOUT",
        "LLM_TEMPERATURE",
        "LLM_TOP_P",
        "RETRIEVAL_EMBED_PROVIDER",
        "RETRIEVAL_EMBED_MODEL",
        "RETRIEVAL_EMBED_DEVICE",
        "RETRIEVAL_EMBED_BATCH_SIZE",
        "RETRIEVAL_EMBED_NORMALIZE",
        "RETRIEVAL_CHUNK_TARGET_TOKENS",
        "RETRIEVAL_CHUNK_OVERLAP_TOKENS",
        "RETRIEVAL_CHARS_PER_TOKEN",
        "MODEL_CALL_LOG_DIR",
        "MODEL_METERING_ENABLED",
        "STT_MODEL",
        "STT_DEVICE",
        "STT_COMPUTE_TYPE",
        "STT_BEAM_SIZE",
        "STT_MAX_AUDIO_MB",
        "STT_VAD_FILTER",
        "STT_CACHE_DIR",
    ]
    for key in keys:
        if os.getenv(key, "").strip():
            continue
        value = secrets.get(key, "").strip()
        if value:
            os.environ[key] = value


_apply_local_secrets_to_env()


def _resolve_agent_root() -> str:
    env_root = os.getenv("LITTLE_ANGEL_AGENT_WORKSPACE", "").strip()
    if env_root:
        return str(Path(env_root).resolve())
    return str((PROJECT_ROOT / "agent_workspace").resolve())


def _resolve_history_dir() -> str:
    return str((PROJECT_ROOT / "chat_history").resolve())


@asynccontextmanager
async def lifespan(app: FastAPI):
    history_dir = _resolve_history_dir()
    agent_root = _resolve_agent_root()
    skills_dir = str((PROJECT_ROOT / "skills").resolve())

    model_manager = ModelConfigManager(str(LOCAL_SECRETS_PATH))
    model_manager.apply_active_profile()
    skills_catalog = SkillsCatalog(skills_dir)

    runtime = BotRuntime(
        history_dir=history_dir,
        agent_root=agent_root,
        max_rounds=20,
        max_steps=20,
        web_user_id="web:local",
    )

    data_dir = HERE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    retrieval_data_dir = (PROJECT_ROOT / "retrieval_core" / "data").resolve()
    search_engine = RetrievalEngine(
        history_dir=history_dir,
        data_dir=str(retrieval_data_dir),
    )
    metering_log_dir = os.getenv("MODEL_CALL_LOG_DIR", "").strip() or str((PROJECT_ROOT / "model_call_logs").resolve())
    metering_engine = get_default_engine(metering_log_dir)
    speech_cache_dir = os.getenv("STT_CACHE_DIR", "").strip() or str((PROJECT_ROOT / "agent_workspace" / ".stt_cache").resolve())
    speech_transcriber = LocalSpeechTranscriber(speech_cache_dir)

    channel_store = ChannelConfigStore(data_path=str(data_dir / "channels.json"))
    channel_runtime = ChannelRuntimeManager(log_dir=str(data_dir / "channel_logs"))
    channel_service = ChannelService(
        project_root=str(PROJECT_ROOT),
        secrets_path=str(LOCAL_SECRETS_PATH),
        config_store=channel_store,
        runtime_manager=channel_runtime,
        specs=default_channel_specs(),
    )

    cron_engine = CronEngine(runtime=runtime, data_path=str(data_dir / "cron_jobs.json"))
    heartbeat_engine = HeartbeatEngine(runtime=runtime, data_path=str(data_dir / "heartbeat.json"))
    search_engine.start()

    cron_engine.start()
    heartbeat_engine.start()

    app.state.runtime = runtime
    app.state.cron_engine = cron_engine
    app.state.heartbeat_engine = heartbeat_engine
    app.state.model_manager = model_manager
    app.state.channel_service = channel_service
    app.state.skills_catalog = skills_catalog
    app.state.search_engine = search_engine
    app.state.metering_engine = metering_engine
    app.state.speech_transcriber = speech_transcriber

    try:
        yield
    finally:
        channel_service.shutdown()
        heartbeat_engine.stop()
        cron_engine.stop()
        search_engine.stop()


app = FastAPI(title="LittleAngel Console", version="1.0.0", lifespan=lifespan)

# Local-only service by default; CORS kept permissive for local tooling.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache_static(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path or ""
    if path == "/" or path.startswith("/assets/") or path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(channels_router)
app.include_router(files_router)
app.include_router(cron_router)
app.include_router(heartbeat_router)
app.include_router(skills_router)
app.include_router(mcp_router)
app.include_router(models_router)
app.include_router(search_router)
app.include_router(billing_router)
app.include_router(speech_router)


@app.get("/api/v1/health")
def health():
    return {"success": True, "service": "littleangel-console"}


WEB_DIR = HERE / "web"
ASSETS_DIR = WEB_DIR / "assets"
INDEX_HTML = WEB_DIR / "index.html"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/")
def web_root():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    raise HTTPException(status_code=404, detail="index_not_found")


@app.get("/{full_path:path}")
def web_spa(full_path: str):
    # Let API routes pass through.
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="not_found")
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    raise HTTPException(status_code=404, detail="index_not_found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("angel_console.app:app", host="127.0.0.1", port=7788, reload=False)
