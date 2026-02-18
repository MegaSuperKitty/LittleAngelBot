# -*- coding: utf-8 -*-
"""Unified LLM provider layer for chat completion style calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple
import json
import os
import urllib.error
import urllib.request

from openai import OpenAI


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


_PROVIDER_CACHE: Dict[Tuple[str, str, str, str, str, Optional[int], float], "_BaseProvider"] = {}


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


def _normalize_provider_name(value: str) -> str:
    text = _strip(value).lower()
    if text in {"anthropic", "claude"}:
        return "anthropic"
    if text in {"dashscope", "qwen"}:
        return "dashscope"
    if text in {"siliconflow", "silicon"}:
        return "siliconflow"
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
    if "siliconflow" in clue:
        return "siliconflow"
    if "openai" in clue:
        return "openai"

    return "openai"


def _provider_kind(provider_name: str) -> str:
    if provider_name == "anthropic":
        return "anthropic"
    return "openai_compatible"


def _default_base_url(provider_name: str) -> str:
    if provider_name == "dashscope":
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if provider_name == "siliconflow":
        return "https://api.siliconflow.cn/v1"
    if provider_name == "anthropic":
        return "https://api.anthropic.com"
    return "https://api.openai.com/v1"


def _default_model(provider_name: str, base_url: str) -> str:
    lower_url = _strip(base_url).lower()
    if provider_name == "dashscope" or "dashscope" in lower_url:
        return "qwen3-max"
    if provider_name == "siliconflow" or "siliconflow" in lower_url:
        return "Qwen/Qwen2.5-7B-Instruct"
    if provider_name == "anthropic" or "anthropic" in lower_url:
        return "claude-3-5-sonnet-latest"
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
    provider_kind = _provider_kind(provider_name)

    resolved_base_url = _first_non_empty(base_url, os.getenv("LLM_BASE_URL", ""), _default_base_url(provider_name))
    resolved_api_key = _first_non_empty(api_key, os.getenv("LLM_API_KEY", ""))

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


def get_response(
    prompts: Sequence[Dict[str, Any]],
    tools: Optional[Sequence[Dict[str, Any]]] = None,
    key_word: str = "",
    stream: bool = False,
    on_token=None,
    temperature: float = 0.0,
    top_p: float = 0.1,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMMessage:
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
        raise RuntimeError(f"Invalid LLM config: {error}")

    backend = _get_provider(config)
    return backend.chat(
        prompts=list(prompts or []),
        tools=list(tools or []),
        key_word=key_word,
        stream=stream,
        on_token=on_token,
        temperature=temperature,
        top_p=top_p,
        model=model or config.model,
        max_tokens=max_tokens if max_tokens is not None else config.max_tokens,
    )


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
            # Keep the current runtime deterministic; tool loops in this repo are non-streaming.
            "stream": False,
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
        message = response.choices[0].message
        return _normalize_openai_message(message)


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
        if stream:
            raise RuntimeError("Anthropic streaming is not implemented in this project.")

        system_text, converted_messages = _to_anthropic_messages(prompts)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": converted_messages,
            "max_tokens": max_tokens or self.config.max_tokens or 2048,
            "temperature": temperature,
            "top_p": top_p,
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
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Anthropic request failed ({exc.code}): {detail}") from exc
        except Exception as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc

        data = json.loads(raw)
        return _normalize_anthropic_message(data)


def _normalize_openai_message(message: Any) -> LLMMessage:
    content = _normalize_content_text(getattr(message, "content", ""))
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
    return LLMMessage(content=content, tool_calls=tool_calls or None)


def _normalize_anthropic_message(data: Dict[str, Any]) -> LLMMessage:
    text_parts: List[str] = []
    tool_calls: List[LLMToolCall] = []
    for index, block in enumerate(data.get("content", []) or []):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(_normalize_content_text(block.get("text", "")))
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
    return LLMMessage(content="".join(text_parts).strip(), tool_calls=tool_calls or None)


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
