# -*- coding: utf-8 -*-
"""Zhipu Web Search MCP tool (streamable HTTP)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import json
import os
import urllib.request
import urllib.error

from tool import Tool


class ZhipuWebSearchTool(Tool):
    """Provide zhipu web search tool capabilities.
    
    Attributes:
        _server_url (Any): Instance field for server url.
        _api_key (Any): Instance field for api key.
        _session_id (Optional[str]): Unique identifier used by the instance.
        _tools_cache (Optional[List[Dict]]): Instance field for tools cache.
        _rpc_id (int): Unique identifier used by the instance.
    """
    def __init__(self):
        """Initialize zhipu web search tool state and dependencies.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        super().__init__(
            name="web_search_zhipu",
            description=(
                "Search the web via Zhipu Web Search MCP (streamable HTTP). "
                "Returns titles, URLs, and summaries when available."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "top_k": {"type": "integer", "description": "Maximum number of results (1-50)."},
                    "recency": {
                        "type": "string",
                        "description": "Time filter: day/week/month/year/none (optional).",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional domain allowlist.",
                    },
                    "summary_level": {
                        "type": "string",
                        "description": "Summary mode: medium or high (optional).",
                    },
                    "engine": {
                        "type": "string",
                        "description": "Engine: webSearchStd/webSearchPro/webSearchSogou/webSearchQuark.",
                    },
                },
                "required": ["query"],
            },
        )
        self._server_url = os.getenv(
            "ZHIPU_WEB_SEARCH_MCP_URL",
            "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp",
        )
        self._api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("BIGMODEL_API_KEY") or ""
        self._session_id: Optional[str] = None
        self._tools_cache: Optional[List[Dict]] = None
        self._rpc_id = 1

    def _execute(self, **kwargs):
        """Internal helper to execute.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        query = (kwargs.get("query") or "").strip()
        if not query:
            return "query 不能为空。"
        if not self._api_key:
            return "未配置 ZHIPU_API_KEY（或 BIGMODEL_API_KEY）。"

        engine = (kwargs.get("engine") or "webSearchPro").strip()
        top_k = kwargs.get("top_k")
        recency = (kwargs.get("recency") or "none").strip().lower()
        domains = kwargs.get("domains") or []
        summary_level = (kwargs.get("summary_level") or "medium").strip().lower()

        self._ensure_session()
        tools = self._list_tools()
        tool_name = _pick_tool_name(engine, tools)

        params = _build_params(query, top_k, recency, domains, summary_level, tools, tool_name)
        result = self._call_tool(tool_name, params)
        return _format_results(result)

    def _ensure_session(self) -> None:
        """Internal helper to ensure session.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        if self._session_id:
            return
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "little-angel-bot", "version": "1.0.0"},
            },
            "id": self._next_id(),
        }
        _, headers = self._post(payload, session_id=None)
        self._session_id = headers.get("mcp-session-id")

    def _list_tools(self) -> List[Dict]:
        """Internal helper to list tools.
        
        Args:
            None.
        
        Returns:
            List[Dict]: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        if self._tools_cache is not None:
            return self._tools_cache
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self._next_id(),
        }
        data, _ = self._post(payload, session_id=self._session_id)
        tools = (data.get("result") or {}).get("tools") or []
        self._tools_cache = tools
        return tools

    def _call_tool(self, name: str, params: Dict) -> Dict:
        """Internal helper to call tool.
        
        Args:
            name (str): Input value for name.
            params (Dict): Input value for params.
        
        Returns:
            Dict: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": params},
            "id": self._next_id(),
        }
        data, _ = self._post(payload, session_id=self._session_id)
        return data.get("result") or {}

    def _post(self, payload: Dict, session_id: Optional[str]) -> Tuple[Dict, Dict[str, str]]:
        """Internal helper to post.
        
        Args:
            payload (Dict): Input value for payload.
            session_id (Optional[str]): Identifier for the session.
        
        Returns:
            Tuple[Dict, Dict[str, str]]: Result produced by this function.
        
        Raises:
            RuntimeError: Raised when an execution error occurs.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self._server_url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("Authorization", _auth_header_value(self._api_key))
        if session_id:
            req.add_header("Mcp-Session-Id", session_id)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                raw = resp.read().decode("utf-8", errors="ignore")
            data = _parse_mcp_response(raw, headers)
            return data, headers
        except urllib.error.HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body_text = ""
            raise RuntimeError(f"HTTP {exc.code}: {body_text}".strip()) from None

    def _next_id(self) -> int:
        """Internal helper to next id.
        
        Args:
            None.
        
        Returns:
            int: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        current = self._rpc_id
        self._rpc_id += 1
        return current


def _pick_tool_name(engine: str, tools: List[Dict]) -> str:
    """Internal helper to pick tool name.
    
    Args:
        engine (str): Input value for engine.
        tools (List[Dict]): Tool definitions or runtime tool bindings.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    names = {t.get("name") for t in tools or []}
    if engine in names:
        return engine
    for fallback in ("webSearchPro", "webSearchStd", "webSearchSogou", "webSearchQuark"):
        if fallback in names:
            return fallback
    return engine or "webSearchPro"


def _build_params(
    query: str,
    top_k: Optional[int],
    recency: str,
    domains: List[str],
    summary_level: str,
    tools: List[Dict],
    tool_name: str,
) -> Dict:
    """Internal helper to build params.
    
    Args:
        query (str): Input value for query.
        top_k (Optional[int]): Input value for top k.
        recency (str): Input value for recency.
        domains (List[str]): Input value for domains.
        summary_level (str): Input value for summary level.
        tools (List[Dict]): Tool definitions or runtime tool bindings.
        tool_name (str): Input value for tool name.
    
    Returns:
        Dict: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    params = {"query": query}
    if top_k:
        params["count"] = int(top_k)
    if recency and recency != "none":
        params["recency"] = recency
    if domains:
        params["domains"] = domains
    if summary_level:
        params["summary_level"] = summary_level

    schema = None
    for tool in tools or []:
        if tool.get("name") == tool_name:
            schema = (tool.get("inputSchema") or {}).get("properties") or {}
            break
    if not schema:
        return params

    mapped: Dict[str, object] = {}
    for key, value in params.items():
        if key in schema:
            mapped[key] = value
    if "q" in schema and "query" in params:
        mapped["q"] = params["query"]
    if "search_query" in schema and "query" in params:
        mapped["search_query"] = params["query"]
    if "top_k" in schema and "count" in params:
        mapped["top_k"] = params["count"]
    if "limit" in schema and "count" in params:
        mapped["limit"] = params["count"]
    if "time_filter" in schema and "recency" in params:
        mapped["time_filter"] = params["recency"]
    return mapped or params


def _format_results(result: Dict) -> str:
    """Internal helper to format results.
    
    Args:
        result (Dict): Input value for result.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if not result:
        return "未返回结果。"
    content = result.get("content")
    if isinstance(content, list):
        for item in content:
            if item.get("type") == "text" and item.get("text"):
                text = item["text"]
                parsed = _try_parse_json(text)
                if parsed is not None:
                    return _format_from_json(parsed)
                return text
    if isinstance(result, dict):
        parsed = _try_parse_json(result)
        if parsed is not None:
            return _format_from_json(parsed)
    return json.dumps(result, ensure_ascii=False)


def _try_parse_json(text):
    """Internal helper to try parse json.
    
    Args:
        text (Any): Text content to process.
    
    Returns:
        Any: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if not text:
        return None
    if isinstance(text, (dict, list)):
        return text
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _format_from_json(data) -> str:
    """Internal helper to format from json.
    
    Args:
        data (Any): Input value for data.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    results = []
    if isinstance(data, dict):
        for key in ("results", "data", "items", "list"):
            if isinstance(data.get(key), list):
                results = data.get(key)
                break
    elif isinstance(data, list):
        results = data

    if not results:
        return json.dumps(data, ensure_ascii=False)

    lines = []
    for idx, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or item.get("name") or "").strip()
        url = (item.get("url") or item.get("link") or "").strip()
        desc = (item.get("summary") or item.get("snippet") or item.get("description") or "").strip()
        line = f"{idx}. {title}\n{url}\n{desc}".strip()
        lines.append(line)
    return "\n\n".join(lines) if lines else json.dumps(data, ensure_ascii=False)


def _parse_mcp_response(raw: str, headers: Dict[str, str]) -> Dict:
    """Internal helper to parse mcp response.
    
    Args:
        raw (str): Input value for raw.
        headers (Dict[str, str]): Input value for headers.
    
    Returns:
        Dict: Result produced by this function.
    
    Raises:
        RuntimeError: Raised when an execution error occurs.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if not raw:
        raise RuntimeError("Empty response body from MCP server.")
    content_type = (headers.get("content-type") or "").lower()
    if "text/event-stream" in content_type or raw.lstrip().startswith("data:"):
        events = _parse_sse_events(raw)
        for event in events:
            data = event.get("data")
            if not data:
                continue
            parsed = _try_parse_json(data)
            if isinstance(parsed, dict):
                return parsed
        raise RuntimeError(f"SSE response did not contain JSON: {raw[:500]}")

    parsed = _try_parse_json(raw)
    if isinstance(parsed, dict):
        return parsed
    raise RuntimeError(f"Non-JSON response: {raw[:500]}")


def _parse_sse_events(raw: str) -> List[Dict[str, str]]:
    """Internal helper to parse sse events.
    
    Args:
        raw (str): Input value for raw.
    
    Returns:
        List[Dict[str, str]]: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    events: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            if current:
                events.append(current)
                current = {}
            continue
        if line.startswith(":"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        events.append(current)
    return events


def _auth_header_value(api_key: str) -> str:
    """Internal helper to auth header value.
    
    Args:
        api_key (str): Input value for api key.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    mode = (os.getenv("ZHIPU_MCP_AUTH_MODE") or "").strip().lower()
    if api_key.lower().startswith("bearer "):
        return api_key
    if mode == "bearer":
        return f"Bearer {api_key}"
    return api_key
