"""Email payload utilities."""

from __future__ import annotations

import base64
from typing import Any, Dict, List

from bs4 import BeautifulSoup


def decode_body(payload: Dict[str, Any]) -> str:
    if not payload:
        return ""
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
    for part in payload.get("parts", []) or []:
        content = decode_body(part)
        if content:
            return content
    return ""


def html_to_text(raw_html: str) -> str:
    return BeautifulSoup(raw_html or "", "html.parser").get_text(separator="\n").strip()


def header(headers: List[Dict[str, str]], name: str) -> str:
    for entry in headers:
        if entry.get("name", "").lower() == name.lower():
            return entry.get("value", "")
    return ""
