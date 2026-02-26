# -*- coding: utf-8 -*-
"""Unified LLM provider layer for chat completion style calls."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Dict, List, Optional, Sequence, Tuple
import json
import os
import threading
import time
import urllib.error
import urllib.request

from openai import OpenAI

from model_metering_core import get_default_engine
from model_metering_core.token_estimator import estimate_usage


@dataclass(frozen=True)
class LLMConfig:
    provider_kind: str
    provider_name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: Optional[int]
    request_timeout: float = 60.0

    def cache_key(self) -> Tuple[str, str, str, str, str, Optional[int], float]:
        return (
            self.provider_kind,
            self.provider_name,
            self.api_key,
            self.base_url,
            self.model,
            self.max_tokens,
            self.request_timeout,
        )


@dataclass
class LLMFunctionCall:
    name: str
    arguments: str


@dataclass
class LLMToolCall:
    id: str
    type: str
    function: LLMFunctionCall


@dataclass
class LLMMessage:
    content: str
    tool_calls: Optional[List[LLMToolCall]] = None
    reasoning_content: str = ""
    usage_prompt_tokens: Optional[int] = None
    usage_completion_tokens: Optional[int] = None
    usage_total_tokens: Optional[int] = None
    usage_source: str = ""
    response_id: str = ""
    finish_reason: str = ""
    latency_ms: Optional[int] = None


_PROVIDER_CACHE: Dict[Tuple[str, str, str, str, str, Optional[int], float], "_BaseProvider"] = {}

_PROVIDER_API_KEY_ENV: Dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
    "openai_custom": "LLM_API_KEY",
    "anthropic_custom": "LLM_API_KEY",
}

_PROVIDER_DISPLAY_NAME: Dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "dashscope": "DashScope",
    "openai_custom": "OpenAI Compatible Endpoint",
    "anthropic_custom": "Anthropic Compatible Endpoint",
}


def _strip(value: Optional[str]) -> str:
    return (value or "").strip()


def _first_non_empty(*values: Optional[str]) -> str:
    for value in values:
        text = _strip(value)
        if text:
            return text
    return ""


def _parse_int(value: Optional[str]) -> Optional[int]:
    text = _strip(value)
    if not text:
        return None
    try:
        return int(text)
    except Exception:
        return None


def _parse_float(value: Optional[str], default: float) -> float:
    text = _strip(value)
    if not text:
        return default
    try:
        return float(text)
    except Exception:
        return default


def _parse_int_like(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _normalize_provider_name(value: str) -> str:
    text = _strip(value).lower()
    if text in {"anthropic_custom", "anthropic-compatible", "anthropic_compatible"}:
        return "anthropic_custom"
    if text in {"anthropic", "claude"}:
        return "anthropic"
    if text in {"openai_custom", "openai-compatible", "openai_compatible"}:
        return "openai_custom"
    if text in {"dashscope", "qwen"}:
        return "dashscope"
    if text in {"openai", "openai_compatible"}:
        return "openai"
    return ""


def _infer_provider_name(provider_hint: str, base_url: str, api_key: str, model: str) -> str:
    explicit = _normalize_provider_name(provider_hint)
    if explicit:
        return explicit

    clue = " ".join([_strip(base_url).lower(), _strip(model).lower()])
    if "anthropic" in clue or "claude" in clue or _strip(api_key).lower().startswith("sk-ant-"):
        return "anthropic"
    if "dashscope" in clue:
        return "dashscope"
    if "openai" in clue:
        return "openai"

    return "openai"


def _provider_kind(provider_name: str) -> str:
    if provider_name in {"anthropic", "anthropic_custom"}:
        return "anthropic"
    return "openai_compatible"


def provider_api_key_env(provider_name: str) -> str:
    return _PROVIDER_API_KEY_ENV.get(_normalize_provider_name(provider_name), "LLM_API_KEY")


def list_provider_catalog() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for provider_name in ["openai", "anthropic", "dashscope", "openai_custom", "anthropic_custom"]:
        rows.append(
            {
                "provider": provider_name,
                "display_name": _PROVIDER_DISPLAY_NAME.get(provider_name, provider_name),
                "api_key_env": provider_api_key_env(provider_name),
                "default_base_url": _default_base_url(provider_name),
                "default_model": _default_model(provider_name, _default_base_url(provider_name)),
                "is_custom": provider_name in {"openai_custom", "anthropic_custom"},
            }
        )
    return rows


def _default_base_url(provider_name: str) -> str:
    if provider_name == "openai":
        return "https://api.openai.com/v1"
    if provider_name == "anthropic":
        return "https://api.anthropic.com"
    if provider_name == "dashscope":
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if provider_name in {"openai_custom", "anthropic_custom"}:
        return ""
    return "https://api.openai.com/v1"


def _default_model(provider_name: str, base_url: str) -> str:
    lower_url = _strip(base_url).lower()
    if provider_name in {"anthropic", "anthropic_custom"} or "anthropic" in lower_url:
        return "claude-3-5-sonnet-latest"
    if provider_name == "dashscope" or "dashscope" in lower_url:
        return "qwen3-max"
    return "gpt-4o-mini"


def resolve_llm_config(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMConfig:
    provider_hint = _first_non_empty(provider, os.getenv("LLM_PROVIDER", ""))
    base_url_hint = _first_non_empty(base_url, os.getenv("LLM_BASE_URL", ""))
    api_key_hint = _first_non_empty(api_key, os.getenv("LLM_API_KEY", ""))
    model_hint = _first_non_empty(model, os.getenv("LLM_MODEL", ""))

    provider_name = _infer_provider_name(provider_hint, base_url_hint, api_key_hint, model_hint)
    # If no explicit hints are given, try provider-specific keys before defaulting.
    if not _strip(provider_hint) and not _strip(base_url_hint) and not _strip(model_hint) and not _strip(api_key_hint):
        for candidate in ["openai", "anthropic", "dashscope"]:
            env_name = provider_api_key_env(candidate)
            if _strip(os.getenv(env_name, "")):
                provider_name = candidate
                break
    provider_kind = _provider_kind(provider_name)

    resolved_base_url = _first_non_empty(base_url, os.getenv("LLM_BASE_URL", ""), _default_base_url(provider_name))
    provider_env_name = provider_api_key_env(provider_name)
    resolved_api_key = _first_non_empty(api_key, os.getenv("LLM_API_KEY", ""), os.getenv(provider_env_name, ""))

    resolved_model = _first_non_empty(model, os.getenv("LLM_MODEL", ""))
    if not resolved_model:
        resolved_model = _default_model(provider_name, resolved_base_url)

    resolved_max_tokens = max_tokens if max_tokens is not None else _parse_int(os.getenv("LLM_MAX_TOKENS", ""))
    if provider_kind == "anthropic" and resolved_max_tokens is None:
        resolved_max_tokens = 2048

    timeout = _parse_float(os.getenv("LLM_TIMEOUT", ""), 60.0)
    return LLMConfig(
        provider_kind=provider_kind,
        provider_name=provider_name,
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        model=resolved_model,
        max_tokens=resolved_max_tokens,
        request_timeout=timeout,
    )


def validate_llm_config(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    config = resolve_llm_config(provider=provider, base_url=base_url, api_key=api_key, model=model)
    if not _strip(config.api_key):
        return "missing api_key (set LLM_API_KEY)"
    return None


def is_llm_configured(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    return validate_llm_config(provider=provider, base_url=base_url, api_key=api_key, model=model) is None


def _jsonable(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        return str(value)


def _clip_text(value: Any, limit: int = 600) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _tool_calls_to_dict(tool_calls: Optional[List[LLMToolCall]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for call in tool_calls or []:
        if isinstance(call, dict):
            rows.append(_jsonable(call))
            continue
        fn = getattr(call, "function", None)
        rows.append(
            {
                "id": str(getattr(call, "id", "") or ""),
                "type": str(getattr(call, "type", "function") or "function"),
                "function": {
                    "name": str(getattr(fn, "name", "") or ""),
                    "arguments": str(getattr(fn, "arguments", "") or ""),
                },
            }
        )
    return rows


def _resolve_caller() -> Dict[str, Any]:
    try:
        for frame in inspect.stack()[1:]:
            path = os.path.abspath(frame.filename)
            if os.path.abspath(__file__) == path:
                continue
            return {
                "file": path,
                "func": frame.function,
                "line": int(frame.lineno),
            }
    except Exception:
        pass
    return {"file": "", "func": "", "line": 0}


def _resolve_profile_id() -> str:
    return _strip(os.getenv("LLM_PROFILE_ID", ""))


def _metering_enabled() -> bool:
    flag = _strip(os.getenv("MODEL_METERING_ENABLED", "1")).lower()
    return flag not in {"0", "false", "off", "no"}


def _metering_engine():
    if not _metering_enabled():
        return None
    try:
        return get_default_engine()
    except Exception:
        return None


def get_response(
    prompts: Sequence[Dict[str, Any]],
    tools: Optional[Sequence[Dict[str, Any]]] = None,
    key_word: str = "",
    stream: bool = False,
    on_token=None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMMessage:
    started_at = time.time()
    config = resolve_llm_config(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
    )
    error = validate_llm_config(
        provider=config.provider_name,
        base_url=config.base_url,
        api_key=config.api_key,
        model=config.model,
    )
    if error:
        exc = RuntimeError(f"Invalid LLM config: {error}")
        engine = _metering_engine()
        if engine is not None:
            finished_at = time.time()
            caller = _resolve_caller()
            engine.record_call(
                {
                    "call_id": engine.build_call_id(started_at),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                    "success": False,
                    "latency_ms": int(max(0.0, (finished_at - started_at) * 1000)),
                    "provider": config.provider_name,
                    "provider_kind": config.provider_kind,
                    "model": config.model,
                    "base_url": config.base_url,
                    "profile_id": _resolve_profile_id(),
                    "stream": bool(stream),
                    "key_word": key_word,
                    "message_count": len(list(prompts or [])),
                    "tool_count": len(list(tools or [])),
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "source": "estimated",
                    },
                    "request_payload": {
                        "messages": _jsonable(list(prompts or [])),
                        "tools": _jsonable(list(tools or [])),
                        "model_params": _jsonable(
                            {
                                "temperature": temperature,
                                "top_p": top_p,
                                "max_tokens": max_tokens,
                                "stream": bool(stream),
                                "key_word": key_word,
                            }
                        ),
                    },
                    "response_payload": {
                        "content": "",
                        "tool_calls": [],
                        "finish_reason": "",
                        "response_id": "",
                    },
                    "input_preview": _clip_text(
                        " ".join(str((m or {}).get("content", "")) for m in list(prompts or []) if isinstance(m, dict))
                    ),
                    "output_preview": "",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "caller_file": caller["file"],
                    "caller_func": caller["func"],
                    "caller_line": caller["line"],
                    "process_id": os.getpid(),
                    "thread_id": threading.get_ident(),
                }
            )
        raise exc

    resolved_temperature = float(temperature) if temperature is not None else _parse_float(os.getenv("LLM_TEMPERATURE", ""), 0.0)
    resolved_top_p = float(top_p) if top_p is not None else _parse_float(os.getenv("LLM_TOP_P", ""), 0.1)
    resolved_model = model or config.model
    resolved_max_tokens = max_tokens if max_tokens is not None else config.max_tokens
    prompts_list = list(prompts or [])
    tools_list = list(tools or [])
    caller = _resolve_caller()
    profile_id = _resolve_profile_id()
    engine = _metering_engine()
    call_id = ""
    if engine is not None:
        try:
            call_id = engine.build_call_id(started_at)
        except Exception:
            call_id = ""

    model_params = {
        "temperature": resolved_temperature,
        "top_p": resolved_top_p,
        "max_tokens": resolved_max_tokens,
        "stream": bool(stream),
        "key_word": key_word,
    }

    backend = _get_provider(config)
    try:
        message = backend.chat(
            prompts=prompts_list,
            tools=tools_list,
            key_word=key_word,
            stream=stream,
            on_token=on_token,
            temperature=resolved_temperature,
            top_p=resolved_top_p,
            model=resolved_model,
            max_tokens=resolved_max_tokens,
        )
    except Exception as exc:
        finished_at = time.time()
        if engine is not None:
            engine.record_call(
                {
                    "call_id": call_id or engine.build_call_id(started_at),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                    "success": False,
                    "latency_ms": int(max(0.0, (finished_at - started_at) * 1000)),
                    "provider": config.provider_name,
                    "provider_kind": config.provider_kind,
                    "model": resolved_model,
                    "base_url": config.base_url,
                    "profile_id": profile_id,
                    "stream": bool(stream),
                    "key_word": key_word,
                    "message_count": len(prompts_list),
                    "tool_count": len(tools_list),
                    "temperature": resolved_temperature,
                    "top_p": resolved_top_p,
                    "max_tokens": resolved_max_tokens,
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "source": "estimated",
                    },
                    "request_payload": {
                        "messages": _jsonable(prompts_list),
                        "tools": _jsonable(tools_list),
                        "model_params": _jsonable(model_params),
                    },
                    "response_payload": {
                        "content": "",
                        "tool_calls": [],
                        "finish_reason": "",
                        "response_id": "",
                    },
                    "input_preview": _clip_text(" ".join(str((m or {}).get("content", "")) for m in prompts_list if isinstance(m, dict))),
                    "output_preview": "",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "caller_file": caller["file"],
                    "caller_func": caller["func"],
                    "caller_line": caller["line"],
                    "process_id": os.getpid(),
                    "thread_id": threading.get_ident(),
                }
            )
        raise

    finished_at = time.time()
    message.latency_ms = int(max(0.0, (finished_at - started_at) * 1000))

    usage_missing = (
        message.usage_prompt_tokens is None
        or message.usage_completion_tokens is None
        or message.usage_total_tokens is None
    )
    if usage_missing:
        estimated = estimate_usage(
            prompts=prompts_list,
            tools=tools_list,
            model_params=model_params,
            response_content=message.content,
            response_tool_calls=_tool_calls_to_dict(message.tool_calls),
        )
        message.usage_prompt_tokens = estimated.prompt_tokens
        message.usage_completion_tokens = estimated.completion_tokens
        message.usage_total_tokens = estimated.total_tokens
        message.usage_source = "estimated"
    else:
        if not message.usage_source:
            message.usage_source = "provider"
        if message.usage_total_tokens is None:
            message.usage_total_tokens = int(message.usage_prompt_tokens or 0) + int(message.usage_completion_tokens or 0)

    if engine is not None:
        engine.record_call(
            {
                "call_id": call_id or engine.build_call_id(started_at),
                "started_at": started_at,
                "finished_at": finished_at,
                "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                "success": True,
                "latency_ms": int(message.latency_ms or 0),
                "provider": config.provider_name,
                "provider_kind": config.provider_kind,
                "model": resolved_model,
                "base_url": config.base_url,
                "profile_id": profile_id,
                "stream": bool(stream),
                "key_word": key_word,
                "message_count": len(prompts_list),
                "tool_count": len(tools_list),
                "temperature": resolved_temperature,
                "top_p": resolved_top_p,
                "max_tokens": resolved_max_tokens,
                "usage": {
                    "prompt_tokens": int(message.usage_prompt_tokens or 0),
                    "completion_tokens": int(message.usage_completion_tokens or 0),
                    "total_tokens": int(message.usage_total_tokens or 0),
                    "source": message.usage_source or "estimated",
                },
                "request_payload": {
                    "messages": _jsonable(prompts_list),
                    "tools": _jsonable(tools_list),
                    "model_params": _jsonable(model_params),
                },
                "response_payload": {
                    "content": message.content or "",
                    "tool_calls": _tool_calls_to_dict(message.tool_calls),
                    "finish_reason": message.finish_reason or "",
                    "response_id": message.response_id or "",
                },
                "input_preview": _clip_text(" ".join(str((m or {}).get("content", "")) for m in prompts_list if isinstance(m, dict))),
                "output_preview": _clip_text(message.content or ""),
                "error_type": "",
                "error_message": "",
                "caller_file": caller["file"],
                "caller_func": caller["func"],
                "caller_line": caller["line"],
                "process_id": os.getpid(),
                "thread_id": threading.get_ident(),
            }
        )

    return message


def _get_provider(config: LLMConfig) -> "_BaseProvider":
    cache_key = config.cache_key()
    cached = _PROVIDER_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if config.provider_kind == "anthropic":
        instance: _BaseProvider = _AnthropicProvider(config)
    else:
        instance = _OpenAICompatibleProvider(config)
    _PROVIDER_CACHE[cache_key] = instance
    return instance


class _BaseProvider:
    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        raise NotImplementedError


class _OpenAICompatibleProvider(_BaseProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        kwargs: Dict[str, Any] = {"api_key": config.api_key}
        if _strip(config.base_url):
            kwargs["base_url"] = config.base_url
        self.client = OpenAI(**kwargs)

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": prompts,
            # Always receive model output via stream and aggregate chunks.
            "stream": True,
            "temperature": temperature,
            "top_p": top_p,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if key_word:
            payload["stop"] = key_word
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**payload)
        return _collect_openai_stream_response(
            response,
            on_token=on_token if stream else None,
        )


class _AnthropicProvider(_BaseProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.endpoint = _build_anthropic_endpoint(config.base_url)

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        system_text, converted_messages = _to_anthropic_messages(prompts)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": converted_messages,
            "max_tokens": max_tokens or self.config.max_tokens or 2048,
            "temperature": temperature,
            "top_p": top_p,
            # Always receive model output via stream and aggregate chunks.
            "stream": True,
        }
        if system_text:
            payload["system"] = system_text

        converted_tools = _to_anthropic_tools(tools)
        if converted_tools:
            payload["tools"] = converted_tools

        if key_word:
            payload["stop_sequences"] = [key_word]

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "content-type": "application/json",
                "accept": "text/event-stream",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout) as response:
                return _collect_anthropic_stream_response(
                    response,
                    on_token=on_token if stream else None,
                )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Anthropic request failed ({exc.code}): {detail}") from exc
        except Exception as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc

 
def _collect_openai_stream_response(response: Any, on_token=None) -> LLMMessage:
    content_parts: List[str] = []
    reasoning_text = ""
    tool_calls_by_index: Dict[int, Dict[str, str]] = {}

    response_id = ""
    finish_reason = ""
    usage_prompt_tokens: Optional[int] = None
    usage_completion_tokens: Optional[int] = None
    usage_total_tokens: Optional[int] = None

    for chunk in response:
        if not response_id:
            response_id = _normalize_content_text(getattr(chunk, "id", ""))

        usage = getattr(chunk, "usage", None)
        if usage is not None:
            usage_prompt_tokens = _parse_int_like(getattr(usage, "prompt_tokens", usage_prompt_tokens or 0))
            usage_completion_tokens = _parse_int_like(getattr(usage, "completion_tokens", usage_completion_tokens or 0))
            usage_total_tokens = _parse_int_like(getattr(usage, "total_tokens", usage_total_tokens or 0))

        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        choice = choices[0]
        if getattr(choice, "finish_reason", None):
            finish_reason = _normalize_content_text(getattr(choice, "finish_reason", ""))

        delta = getattr(choice, "delta", None)
        if delta is None:
            continue

        raw_content = getattr(delta, "content", None)
        text_delta = _normalize_text_content(raw_content)
        if text_delta:
            content_parts.append(text_delta)
            _safe_on_token(on_token, text_delta)

        reasoning_delta = _normalize_reasoning_text(
            getattr(delta, "reasoning_content", "")
            or getattr(delta, "reasoning", "")
            or getattr(delta, "thinking", "")
        )
        if not reasoning_delta:
            reasoning_delta = _normalize_reasoning_from_content_blocks(raw_content)
        if reasoning_delta:
            reasoning_text = _merge_reasoning_fragment(reasoning_text, reasoning_delta)

        delta_tool_calls = getattr(delta, "tool_calls", None) or []
        for idx, call in enumerate(delta_tool_calls):
            call_index = _parse_int_like(getattr(call, "index", idx), idx)
            slot = tool_calls_by_index.setdefault(
                call_index,
                {
                    "id": "",
                    "type": "function",
                    "name": "",
                    "arguments": "",
                },
            )
            slot["id"] = _merge_stream_fragment(slot["id"], _normalize_content_text(getattr(call, "id", "")))
            slot["type"] = _merge_stream_fragment(
                slot["type"],
                _normalize_content_text(getattr(call, "type", "function")) or "function",
            )
            function = getattr(call, "function", None)
            if function is not None:
                slot["name"] = _merge_stream_fragment(
                    slot["name"],
                    _normalize_content_text(getattr(function, "name", "")),
                )
                slot["arguments"] = _merge_stream_fragment(
                    slot["arguments"],
                    _normalize_content_text(getattr(function, "arguments", "")),
                )

    calls: List[LLMToolCall] = []
    for idx in sorted(tool_calls_by_index.keys()):
        item = tool_calls_by_index[idx]
        call_id = _normalize_content_text(item.get("id", "")) or f"call_{idx + 1}"
        call_type = _normalize_content_text(item.get("type", "function")) or "function"
        call_name = _normalize_content_text(item.get("name", ""))
        call_arguments = item.get("arguments", "").strip() or "{}"
        calls.append(
            LLMToolCall(
                id=call_id,
                type=call_type,
                function=LLMFunctionCall(name=call_name, arguments=call_arguments),
            )
        )

    normalized = LLMMessage(
        content="".join(content_parts),
        tool_calls=calls or None,
        reasoning_content=reasoning_text.strip(),
    )
    normalized.response_id = response_id
    normalized.finish_reason = finish_reason
    if usage_prompt_tokens is not None or usage_completion_tokens is not None or usage_total_tokens is not None:
        p = int(usage_prompt_tokens or 0)
        c = int(usage_completion_tokens or 0)
        t = int(usage_total_tokens or (p + c))
        normalized.usage_prompt_tokens = p
        normalized.usage_completion_tokens = c
        normalized.usage_total_tokens = t
        normalized.usage_source = "provider"
    return normalized


def _collect_anthropic_stream_response(response: Any, on_token=None) -> LLMMessage:
    response_id = ""
    finish_reason = ""
    text_parts: List[str] = []
    reasoning_text = ""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    tool_calls_by_index: Dict[int, Dict[str, str]] = {}

    for event_name, data in _iter_sse_json_events(response):
        if not isinstance(data, dict):
            continue

        event_type = event_name
        if event_type == "message":
            event_type = _normalize_content_text(data.get("type", "")) or event_type

        if event_type == "error":
            detail = data.get("error", data)
            if isinstance(detail, dict):
                msg = _normalize_content_text(detail.get("message", "")) or json.dumps(detail, ensure_ascii=False)
            else:
                msg = _normalize_content_text(detail)
            raise RuntimeError(f"Anthropic stream error: {msg}")

        if event_type == "message_start":
            message = data.get("message") or {}
            if isinstance(message, dict):
                response_id = _normalize_content_text(message.get("id", "")) or response_id
                usage = message.get("usage") or {}
                if isinstance(usage, dict):
                    prompt_tokens = _parse_int_like(
                        usage.get("input_tokens", usage.get("prompt_tokens", prompt_tokens or 0))
                    )
                    output_guess = usage.get("output_tokens", usage.get("completion_tokens", completion_tokens))
                    if output_guess is not None:
                        completion_tokens = _parse_int_like(output_guess, completion_tokens or 0)
                    total_guess = usage.get("total_tokens")
                    if total_guess is not None:
                        total_tokens = _parse_int_like(total_guess, total_tokens or 0)
            continue

        if event_type == "content_block_start":
            block_index = _parse_int_like(data.get("index"), 0)
            block = data.get("content_block") or {}
            if not isinstance(block, dict):
                block = {}
            block_type = _normalize_content_text(block.get("type", "")).lower()
            if block_type == "text":
                text = _normalize_content_text(block.get("text", ""))
                if text:
                    text_parts.append(text)
                    _safe_on_token(on_token, text)
            elif block_type in {"thinking", "reasoning"}:
                reason = _normalize_reasoning_text(
                    block.get("thinking", "")
                    or block.get("reasoning", "")
                    or block.get("text", "")
                )
                if reason:
                    reasoning_text = _merge_reasoning_fragment(reasoning_text, reason)
            elif block_type == "tool_use":
                slot = tool_calls_by_index.setdefault(
                    block_index,
                    {
                        "id": "",
                        "type": "function",
                        "name": "",
                        "arguments": "",
                    },
                )
                slot["id"] = _merge_stream_fragment(slot["id"], _normalize_content_text(block.get("id", "")))
                slot["name"] = _merge_stream_fragment(slot["name"], _normalize_content_text(block.get("name", "")))
                raw_input = block.get("input")
                if raw_input is not None:
                    slot["arguments"] = _merge_stream_fragment(slot["arguments"], _stringify_arguments(raw_input))
            continue

        if event_type == "content_block_delta":
            block_index = _parse_int_like(data.get("index"), 0)
            delta = data.get("delta") or {}
            if not isinstance(delta, dict):
                delta = {}
            delta_type = _normalize_content_text(delta.get("type", "")).lower()
            if delta_type == "text_delta":
                text = _normalize_content_text(delta.get("text", ""))
                if text:
                    text_parts.append(text)
                    _safe_on_token(on_token, text)
            elif delta_type in {"thinking_delta", "reasoning_delta"}:
                reason = _normalize_reasoning_text(
                    delta.get("thinking", "")
                    or delta.get("reasoning", "")
                    or delta.get("text", "")
                )
                if reason:
                    reasoning_text = _merge_reasoning_fragment(reasoning_text, reason)
            elif delta_type == "input_json_delta":
                slot = tool_calls_by_index.setdefault(
                    block_index,
                    {
                        "id": "",
                        "type": "function",
                        "name": "",
                        "arguments": "",
                    },
                )
                partial = _normalize_content_text(delta.get("partial_json", ""))
                slot["arguments"] = _merge_stream_fragment(slot["arguments"], partial)
            continue

        if event_type == "message_delta":
            delta = data.get("delta") or {}
            usage = data.get("usage") or {}
            if isinstance(delta, dict):
                reason = _normalize_content_text(delta.get("stop_reason", ""))
                if reason:
                    finish_reason = reason
            if isinstance(usage, dict):
                output_guess = usage.get("output_tokens", usage.get("completion_tokens", completion_tokens))
                if output_guess is not None:
                    completion_tokens = _parse_int_like(output_guess, completion_tokens or 0)
                total_guess = usage.get("total_tokens")
                if total_guess is not None:
                    total_tokens = _parse_int_like(total_guess, total_tokens or 0)
            continue

        if event_type == "message_stop":
            break

    calls: List[LLMToolCall] = []
    for idx in sorted(tool_calls_by_index.keys()):
        item = tool_calls_by_index[idx]
        call_id = _normalize_content_text(item.get("id", "")) or f"toolu_{idx + 1}"
        call_name = _normalize_content_text(item.get("name", ""))
        call_arguments = item.get("arguments", "").strip() or "{}"
        calls.append(
            LLMToolCall(
                id=call_id,
                type="function",
                function=LLMFunctionCall(name=call_name, arguments=call_arguments),
            )
        )

    normalized = LLMMessage(
        content="".join(text_parts).strip(),
        tool_calls=calls or None,
        reasoning_content=reasoning_text.strip(),
    )
    normalized.response_id = response_id
    normalized.finish_reason = finish_reason
    if prompt_tokens is not None or completion_tokens is not None or total_tokens is not None:
        p = int(prompt_tokens or 0)
        c = int(completion_tokens or 0)
        t = int(total_tokens or (p + c))
        normalized.usage_prompt_tokens = p
        normalized.usage_completion_tokens = c
        normalized.usage_total_tokens = t
        normalized.usage_source = "provider"
    return normalized


def _iter_sse_json_events(response: Any):
    event_name = "message"
    data_lines: List[str] = []

    while True:
        raw_line = response.readline()
        if raw_line in {b"", ""}:
            if data_lines:
                payload = "\n".join(data_lines).strip()
                if payload:
                    try:
                        yield event_name, json.loads(payload)
                    except Exception:
                        pass
            break

        if isinstance(raw_line, bytes):
            line = raw_line.decode("utf-8", errors="ignore")
        else:
            line = str(raw_line)
        line = line.rstrip("\r\n")

        if line.startswith(":"):
            continue

        if line == "":
            if data_lines:
                payload = "\n".join(data_lines).strip()
                if payload:
                    try:
                        yield event_name, json.loads(payload)
                    except Exception:
                        pass
            event_name = "message"
            data_lines = []
            continue

        if line.startswith("event:"):
            event_name = line[6:].strip() or "message"
            continue

        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip(" "))
            continue


def _safe_on_token(on_token, token: str) -> None:
    if not callable(on_token):
        return
    if not token:
        return
    try:
        on_token(token)
    except Exception:
        pass


def _merge_stream_fragment(existing: str, fragment: str) -> str:
    base = existing or ""
    piece = fragment or ""
    if not piece:
        return base
    if not base:
        return piece
    if piece.startswith(base):
        return piece
    if base.endswith(piece):
        return base
    return base + piece


def _merge_reasoning_fragment(existing: str, fragment: str) -> str:
    base = (existing or "").strip()
    piece = (fragment or "").strip()
    if not piece:
        return base
    if not base:
        return piece
    merged = _merge_stream_fragment(base, piece)
    if merged != base:
        return merged
    return base


def _normalize_openai_message(message: Any) -> LLMMessage:
    content = _normalize_content_text(getattr(message, "content", ""))
    reasoning_content = _normalize_reasoning_text(getattr(message, "reasoning_content", ""))
    if not reasoning_content:
        reasoning_content = _normalize_reasoning_from_content_blocks(getattr(message, "content", None))
    tool_calls: List[LLMToolCall] = []
    for index, call in enumerate(getattr(message, "tool_calls", None) or []):
        function = getattr(call, "function", None)
        if function is None:
            continue
        name = _normalize_content_text(getattr(function, "name", ""))
        raw_arguments = getattr(function, "arguments", "")
        arguments = _stringify_arguments(raw_arguments)
        call_id = _normalize_content_text(getattr(call, "id", "")) or f"call_{index + 1}"
        call_type = _normalize_content_text(getattr(call, "type", "function")) or "function"
        tool_calls.append(
            LLMToolCall(
                id=call_id,
                type=call_type,
                function=LLMFunctionCall(name=name, arguments=arguments),
            )
        )
    return LLMMessage(
        content=content,
        tool_calls=tool_calls or None,
        reasoning_content=reasoning_content,
    )


def _normalize_anthropic_message(data: Dict[str, Any]) -> LLMMessage:
    text_parts: List[str] = []
    reasoning_parts: List[str] = []
    tool_calls: List[LLMToolCall] = []
    for index, block in enumerate(data.get("content", []) or []):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(_normalize_content_text(block.get("text", "")))
            continue
        if block_type in {"thinking", "reasoning"}:
            reasoning_parts.append(
                _normalize_reasoning_text(
                    block.get("thinking", "")
                    or block.get("reasoning", "")
                    or block.get("text", "")
                )
            )
            continue
        if block_type == "tool_use":
            tool_id = _normalize_content_text(block.get("id", "")) or f"toolu_{index + 1}"
            name = _normalize_content_text(block.get("name", ""))
            arguments = _stringify_arguments(block.get("input", {}))
            tool_calls.append(
                LLMToolCall(
                    id=tool_id,
                    type="function",
                    function=LLMFunctionCall(name=name, arguments=arguments),
                )
            )
    return LLMMessage(
        content="".join(text_parts).strip(),
        tool_calls=tool_calls or None,
        reasoning_content="\n".join([part for part in reasoning_parts if part]).strip(),
    )


def _normalize_content_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(_normalize_content_text(item.get("text", "")))
                elif "text" in item:
                    parts.append(_normalize_content_text(item.get("text", "")))
        return "".join(parts)
    return str(content)


def _normalize_text_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            item_type = str(item.get("type", "") or "").strip().lower()
            if item_type in {"text", "output_text", "input_text"}:
                parts.append(_normalize_text_content(item.get("text", "")))
                continue
            if "text" in item and item_type not in {"reasoning", "thinking", "reasoning_content", "tool_call", "tool_calls", "tool_use"}:
                parts.append(_normalize_text_content(item.get("text", "")))
        return "".join(parts)
    if isinstance(content, dict):
        item_type = str(content.get("type", "") or "").strip().lower()
        if item_type in {"text", "output_text", "input_text"}:
            return _normalize_text_content(content.get("text", ""))
        if "text" in content and item_type not in {"reasoning", "thinking", "reasoning_content", "tool_call", "tool_calls", "tool_use"}:
            return _normalize_text_content(content.get("text", ""))
        return ""
    return str(content)


def _normalize_reasoning_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    parts.append(text)
                continue
            if isinstance(item, dict):
                item_type = str(item.get("type", "") or "").strip().lower()
                if item_type in {"thinking", "reasoning", "reasoning_content"}:
                    text = (
                        _normalize_content_text(item.get("thinking", ""))
                        or _normalize_content_text(item.get("reasoning", ""))
                        or _normalize_content_text(item.get("text", ""))
                    ).strip()
                    if text:
                        parts.append(text)
        return "\n".join(parts).strip()
    return str(content).strip()


def _normalize_reasoning_from_content_blocks(content: Any) -> str:
    if not isinstance(content, list):
        return ""
    parts: List[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", "") or "").strip().lower()
        if item_type not in {"thinking", "reasoning", "reasoning_content"}:
            continue
        text = (
            _normalize_content_text(item.get("thinking", ""))
            or _normalize_content_text(item.get("reasoning", ""))
            or _normalize_content_text(item.get("text", ""))
        ).strip()
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _stringify_arguments(arguments: Any) -> str:
    if isinstance(arguments, str):
        return arguments
    if arguments is None:
        return "{}"
    try:
        return json.dumps(arguments, ensure_ascii=False)
    except Exception:
        return str(arguments)


def _to_anthropic_tools(tools: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted: List[Dict[str, Any]] = []
    for item in tools or []:
        if not isinstance(item, dict):
            continue
        if "name" in item and "input_schema" in item:
            converted.append(item)
            continue
        if item.get("type") != "function":
            continue
        fn = item.get("function")
        if not isinstance(fn, dict):
            continue
        name = _normalize_content_text(fn.get("name", ""))
        if not name:
            continue
        schema = fn.get("parameters")
        if not isinstance(schema, dict):
            schema = {"type": "object", "properties": {}}
        converted.append(
            {
                "name": name,
                "description": _normalize_content_text(fn.get("description", "")),
                "input_schema": schema,
            }
        )
    return converted


def _to_anthropic_messages(messages: Sequence[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    system_parts: List[str] = []
    converted: List[Dict[str, Any]] = []

    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = _normalize_content_text(item.get("role", "")).lower()
        if role == "system":
            text = _normalize_content_text(item.get("content", ""))
            if text:
                system_parts.append(text)
            continue

        if role == "tool":
            tool_call_id = _normalize_content_text(item.get("tool_call_id", "")) or "tool_call_id_missing"
            converted.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_call_id,
                            "content": _normalize_content_text(item.get("content", "")),
                        }
                    ],
                }
            )
            continue

        if role == "assistant":
            text = _normalize_content_text(item.get("content", ""))
            tool_calls = item.get("tool_calls") or []
            if tool_calls:
                blocks: List[Dict[str, Any]] = []
                if text:
                    blocks.append({"type": "text", "text": text})
                for index, call in enumerate(tool_calls):
                    call_id, name, arguments = _extract_tool_call(call, index)
                    blocks.append(
                        {
                            "type": "tool_use",
                            "id": call_id,
                            "name": name,
                            "input": _parse_tool_arguments(arguments),
                        }
                    )
                converted.append({"role": "assistant", "content": blocks})
            else:
                converted.append({"role": "assistant", "content": text})
            continue

        converted.append({"role": "user", "content": _normalize_content_text(item.get("content", ""))})

    return "\n\n".join(system_parts).strip(), converted


def _extract_tool_call(call: Any, index: int) -> Tuple[str, str, Any]:
    if isinstance(call, dict):
        fn = call.get("function", {})
        if not isinstance(fn, dict):
            fn = {}
        call_id = _normalize_content_text(call.get("id", "")) or f"call_{index + 1}"
        name = _normalize_content_text(fn.get("name", ""))
        arguments = fn.get("arguments", "{}")
        return call_id, name, arguments

    function = getattr(call, "function", None)
    call_id = _normalize_content_text(getattr(call, "id", "")) or f"call_{index + 1}"
    name = _normalize_content_text(getattr(function, "name", "")) if function is not None else ""
    arguments = getattr(function, "arguments", "{}") if function is not None else "{}"
    return call_id, name, arguments


def _parse_tool_arguments(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {"value": parsed}
        except Exception:
            return {"raw": raw}
    if raw is None:
        return {}
    return {"value": raw}


def _build_anthropic_endpoint(base_url: str) -> str:
    base = _strip(base_url)
    if not base:
        return "https://api.anthropic.com/v1/messages"
    lower = base.lower()
    if lower.endswith("/v1/messages"):
        return base
    if lower.endswith("/v1"):
        return base + "/messages"
    return base.rstrip("/") + "/v1/messages"
