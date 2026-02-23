# -*- coding: utf-8 -*-
"""网页抓取工具（纯 HTTP，不执行 JS）。"""

from __future__ import annotations

from html.parser import HTMLParser
import ipaddress
import urllib.parse
import urllib.request

from tool import Tool


class WebFetchTool(Tool):
    """Represent the WebFetchTool component.
    
    Note:
        This class currently exposes no documented instance attributes.
    """
    def __init__(self):
        """Initialize web fetch tool state and dependencies.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        super().__init__(
            name="web_fetch",
            description="Fetch a web page and extract text (no JS execution).",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch (http/https)."},
                    "max_chars": {"type": "integer", "description": "Maximum chars to return."},
                },
                "required": ["url"],
            },
        )

    def _execute(self, **kwargs):
        """Internal helper to execute.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        url = (kwargs.get("url") or "").strip()
        max_chars = int(kwargs.get("max_chars") or 5000)
        if not _is_safe_url(url):
            return "不允许访问该 URL。"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return "抓取失败。"
        text = _html_to_text(html)
        text = text[: max_chars].strip()
        if not text:
            return "未提取到正文内容。"
        return text


def _is_safe_url(url: str) -> bool:
    """Internal helper to is safe url.
    
    Args:
        url (str): Input value for url.
    
    Returns:
        bool: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname or ""
    if not host:
        return False
    if host.lower() in {"localhost"}:
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        pass
    return True


class _TextExtractor(HTMLParser):
    """Represent the TextExtractor component.
    
    Attributes:
        _parts (Any): Instance field for parts.
    """
    def __init__(self):
        """Initialize text extractor state and dependencies.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        """Handle data.
        
        Args:
            data (Any): Input value for data.
        
        Returns:
            None: This method does not return a value.
        """
        if data:
            self._parts.append(data)

    def get_text(self) -> str:
        """Get text.
        
        Args:
            None.
        
        Returns:
            str: The resolved text value.
        """
        return " ".join(self._parts)


def _html_to_text(html: str) -> str:
    """Internal helper to html to text.
    
    Args:
        html (str): Input value for html.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.get_text()
    return " ".join(text.split())
