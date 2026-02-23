# -*- coding: utf-8 -*-
"""Model profile manager for local_secrets-backed multi-provider config."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import yaml

from llm_provider import get_response, list_provider_catalog, provider_api_key_env, validate_llm_config


@dataclass
class ModelProfile:
    profile_id: str
    provider: str
    base_url: str
    model: str
    api_key: str
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None


def _mask_secret(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if len(text) <= 8:
        return "*" * len(text)
    return f"{text[:3]}{'*' * (len(text) - 6)}{text[-3:]}"


class ModelConfigManager:
    """Persist and apply model profiles backed by local_secrets.yaml."""

    def __init__(self, secrets_path: str):
        self.secrets_path = Path(secrets_path).resolve()
        self._lock = threading.Lock()
        self._catalog = list_provider_catalog()
        self._provider_map = {row["provider"]: row for row in self._catalog}
        self._connectivity_cache: Dict[str, Dict[str, Any]] = {}

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            return self._build_state_locked(active_id, profiles)

    def apply_active_profile(self) -> Dict[str, Any]:
        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            active = profiles.get(active_id)
            if active:
                self._apply_env_locked(active)
            return self._build_state_locked(active_id, profiles)

    def upsert_profile(
        self,
        profile_id: str,
        provider: str,
        base_url: str = "",
        model: str = "",
        api_key: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        clear_api_key: bool = False,
    ) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")

        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)

            existing = profiles.get(pid)
            normalized_provider = self._normalize_provider(provider)
            preset = self._provider_map.get(normalized_provider, self._provider_map["openai"])

            base = (base_url or "").strip() or (existing.base_url if existing else preset["default_base_url"])
            model_name = (model or "").strip() or (existing.model if existing else preset["default_model"])

            if self._provider_requires_custom_base_url(normalized_provider) and not base:
                raise ValueError("base_url is required for custom provider")

            if clear_api_key:
                key_value = ""
            elif api_key is None:
                key_value = existing.api_key if existing else ""
            else:
                key_value = (api_key or "").strip() or (existing.api_key if existing else "")

            if not (key_value or "").strip():
                raise ValueError("api_key is required")

            prof = ModelProfile(
                profile_id=pid,
                provider=normalized_provider,
                base_url=base,
                model=model_name,
                api_key=key_value,
                max_tokens=max_tokens if max_tokens is not None else (existing.max_tokens if existing else None),
                timeout=timeout if timeout is not None else (existing.timeout if existing else None),
                temperature=temperature if temperature is not None else (existing.temperature if existing else None),
                top_p=top_p if top_p is not None else (existing.top_p if existing else None),
            )
            profiles[pid] = prof
            self._connectivity_cache.pop(pid, None)
            if not active_id:
                active_id = pid

            self._write_back_locked(data, active_id, profiles)
            self._save_yaml_locked(data)
            return self._build_state_locked(active_id, profiles)

    def activate_profile(self, profile_id: str) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")

        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            if pid not in profiles:
                raise ValueError("profile not found")
            active_id = pid
            self._write_back_locked(data, active_id, profiles)
            self._save_yaml_locked(data)
            self._apply_env_locked(profiles[active_id])
            return self._build_state_locked(active_id, profiles)

    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")

        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            if pid not in profiles:
                raise ValueError("profile not found")
            profiles.pop(pid, None)
            if not profiles:
                # Keep at least one default profile to avoid a broken state.
                fallback = self._build_default_profile(data)
                profiles[fallback.profile_id] = fallback
            if active_id not in profiles:
                active_id = next(iter(profiles.keys()))
            self._connectivity_cache.pop(pid, None)

            self._write_back_locked(data, active_id, profiles)
            self._save_yaml_locked(data)
            self._apply_env_locked(profiles[active_id])
            return self._build_state_locked(active_id, profiles)

    def test_profile_connectivity(self, profile_id: str) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")

        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            target = profiles.get(pid)
            if target is None:
                raise ValueError("profile not found")

        status = "failed"
        detail = ""
        try:
            response = get_response(
                prompts=[
                    {"role": "system", "content": "You are a connectivity probe."},
                    {"role": "user", "content": "你好"},
                ],
                tools=None,
                stream=False,
                provider=target.provider,
                base_url=target.base_url,
                api_key=target.api_key,
                model=target.model,
                max_tokens=64,
                temperature=target.temperature,
                top_p=target.top_p,
            )
            status = "success"
            detail = (response.content or "").strip()[:200]
        except Exception as exc:
            detail = str(exc)

        with self._lock:
            data = self._read_yaml_locked()
            active_id, profiles = self._load_profiles_locked(data)
            if pid in profiles:
                self._connectivity_cache[pid] = {
                    "status": status,
                    "detail": detail,
                    "checked_at": int(time.time()),
                }
            return self._build_state_locked(active_id, profiles)

    # ---- Internal helpers ----

    def _read_yaml_locked(self) -> Dict[str, Any]:
        if not self.secrets_path.is_file():
            return {}
        try:
            raw = yaml.safe_load(self.secrets_path.read_text(encoding="utf-8")) or {}
            return raw if isinstance(raw, dict) else {}
        except Exception:
            return {}

    def _save_yaml_locked(self, data: Dict[str, Any]) -> None:
        self.secrets_path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        self.secrets_path.write_text(text, encoding="utf-8")

    def _normalize_provider(self, provider: str) -> str:
        text = (provider or "").strip().lower()
        aliases = {
            "claude": "anthropic",
            "qwen": "dashscope",
            "openai_compatible": "openai_custom",
            "openai-compatible": "openai_custom",
            "anthropic_compatible": "anthropic_custom",
            "anthropic-compatible": "anthropic_custom",
        }
        text = aliases.get(text, text)
        if text in self._provider_map:
            return text
        return "openai"

    def _provider_requires_custom_base_url(self, provider: str) -> bool:
        return provider in {"openai_custom", "anthropic_custom"}

    def _parse_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return int(text)
        except Exception:
            return None

    def _parse_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return float(text)
        except Exception:
            return None

    def _build_default_profile(self, data: Dict[str, Any]) -> ModelProfile:
        provider = self._normalize_provider(str(data.get("LLM_PROVIDER", "")).strip() or "openai")
        preset = self._provider_map.get(provider, self._provider_map["openai"])
        env_key = provider_api_key_env(provider)
        api_key = str(data.get("LLM_API_KEY", "") or "").strip() or str(data.get(env_key, "") or "").strip()
        base_url = str(data.get("LLM_BASE_URL", "") or "").strip() or preset["default_base_url"]
        model = str(data.get("LLM_MODEL", "") or "").strip() or preset["default_model"]
        max_tokens = self._parse_int(data.get("LLM_MAX_TOKENS"))
        timeout = self._parse_float(data.get("LLM_TIMEOUT"))
        temperature = self._parse_float(data.get("LLM_TEMPERATURE"))
        top_p = self._parse_float(data.get("LLM_TOP_P"))
        return ModelProfile(
            profile_id="default",
            provider=provider,
            base_url=base_url,
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            timeout=timeout,
            temperature=temperature,
            top_p=top_p,
        )

    def _load_profiles_locked(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, ModelProfile]]:
        node = data.get("LLM_PROFILES", {})
        active = ""
        profiles: Dict[str, ModelProfile] = {}

        if isinstance(node, dict):
            active = str(node.get("active", "") or "").strip()
            raw_profiles = node.get("profiles", {})
            if isinstance(raw_profiles, dict):
                for pid, row in raw_profiles.items():
                    if not isinstance(row, dict):
                        continue
                    profile_id = str(pid or "").strip()
                    if not profile_id:
                        continue
                    provider = self._normalize_provider(str(row.get("provider", "")).strip() or "openai")
                    preset = self._provider_map.get(provider, self._provider_map["openai"])
                    base_url = str(row.get("base_url", "") or "").strip() or preset["default_base_url"]
                    model_name = str(row.get("model", "") or "").strip() or preset["default_model"]
                    api_key = str(row.get("api_key", "") or "").strip()
                    max_tokens = self._parse_int(row.get("max_tokens"))
                    timeout = self._parse_float(row.get("timeout"))
                    temperature = self._parse_float(row.get("temperature"))
                    top_p = self._parse_float(row.get("top_p"))
                    profiles[profile_id] = ModelProfile(
                        profile_id=profile_id,
                        provider=provider,
                        base_url=base_url,
                        model=model_name,
                        api_key=api_key,
                        max_tokens=max_tokens,
                        timeout=timeout,
                        temperature=temperature,
                        top_p=top_p,
                    )

        if not profiles:
            default_profile = self._build_default_profile(data)
            profiles[default_profile.profile_id] = default_profile

        if active not in profiles:
            active = next(iter(profiles.keys()))

        return active, profiles

    def _write_back_locked(self, data: Dict[str, Any], active_id: str, profiles: Dict[str, ModelProfile]) -> None:
        profile_map: Dict[str, Any] = {}
        for pid, row in profiles.items():
            profile_map[pid] = {
                "provider": row.provider,
                "base_url": row.base_url,
                "model": row.model,
                "api_key": row.api_key,
                "max_tokens": row.max_tokens,
                "timeout": row.timeout,
                "temperature": row.temperature,
                "top_p": row.top_p,
            }
        data["LLM_PROFILES"] = {"active": active_id, "profiles": profile_map}

        active = profiles[active_id]
        data["LLM_PROVIDER"] = active.provider
        data["LLM_PROFILE_ID"] = active.profile_id
        data["LLM_BASE_URL"] = active.base_url
        data["LLM_MODEL"] = active.model
        data["LLM_API_KEY"] = active.api_key
        data["LLM_MAX_TOKENS"] = "" if active.max_tokens is None else active.max_tokens
        data["LLM_TIMEOUT"] = "" if active.timeout is None else active.timeout
        data["LLM_TEMPERATURE"] = "" if active.temperature is None else active.temperature
        data["LLM_TOP_P"] = "" if active.top_p is None else active.top_p
        provider_env = provider_api_key_env(active.provider)
        data[provider_env] = active.api_key
        self._apply_env_locked(active)

    def _apply_env_locked(self, active: ModelProfile) -> None:
        os.environ["LLM_PROVIDER"] = active.provider
        os.environ["LLM_PROFILE_ID"] = active.profile_id
        os.environ["LLM_BASE_URL"] = active.base_url
        os.environ["LLM_MODEL"] = active.model
        os.environ["LLM_API_KEY"] = active.api_key
        if active.max_tokens is None:
            os.environ.pop("LLM_MAX_TOKENS", None)
        else:
            os.environ["LLM_MAX_TOKENS"] = str(active.max_tokens)
        if active.timeout is None:
            os.environ.pop("LLM_TIMEOUT", None)
        else:
            os.environ["LLM_TIMEOUT"] = str(active.timeout)
        if active.temperature is None:
            os.environ.pop("LLM_TEMPERATURE", None)
        else:
            os.environ["LLM_TEMPERATURE"] = str(active.temperature)
        if active.top_p is None:
            os.environ.pop("LLM_TOP_P", None)
        else:
            os.environ["LLM_TOP_P"] = str(active.top_p)
        provider_env = provider_api_key_env(active.provider)
        if active.api_key:
            os.environ[provider_env] = active.api_key

    def _build_state_locked(self, active_id: str, profiles: Dict[str, ModelProfile]) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for pid, row in profiles.items():
            connectivity = self._connectivity_cache.get(pid, {"status": "untested", "detail": "", "checked_at": None})
            rows.append(
                {
                    "profile_id": pid,
                    "provider": row.provider,
                    "display_name": self._provider_map.get(row.provider, {}).get("display_name", row.provider),
                    "base_url": row.base_url,
                    "model": row.model,
                    "max_tokens": row.max_tokens,
                    "timeout": row.timeout,
                    "temperature": row.temperature,
                    "top_p": row.top_p,
                    "has_api_key": bool((row.api_key or "").strip()),
                    "api_key_masked": _mask_secret(row.api_key),
                    "active": pid == active_id,
                    "connectivity_status": connectivity.get("status", "untested"),
                    "connectivity_detail": connectivity.get("detail", ""),
                    "connectivity_checked_at": connectivity.get("checked_at"),
                }
            )
        rows.sort(key=lambda item: item["profile_id"])

        provider_rows: List[Dict[str, Any]] = []
        for item in self._catalog:
            provider_name = item["provider"]
            matched = [p for p in rows if p["provider"] == provider_name]
            provider_rows.append(
                {
                    **item,
                    "authorized": any(p["has_api_key"] for p in matched),
                    "active": any(p["active"] for p in matched),
                    "profile_count": len(matched),
                }
            )

        active = profiles.get(active_id)
        runtime_info: Dict[str, Any] = {}
        if active:
            error = validate_llm_config(
                provider=active.provider,
                base_url=active.base_url,
                api_key=active.api_key,
                model=active.model,
            )
            runtime_info = {
                "provider": active.provider,
                "base_url": active.base_url,
                "model": active.model,
                "api_key_masked": _mask_secret(active.api_key),
                "temperature": active.temperature,
                "top_p": active.top_p,
                "valid": error is None,
                "error": error or "",
            }

        return {
            "success": True,
            "active_profile_id": active_id,
            "profiles": rows,
            "providers": provider_rows,
            "runtime": runtime_info,
        }
