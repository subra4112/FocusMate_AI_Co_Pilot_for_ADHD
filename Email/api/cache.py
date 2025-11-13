"""Simple cache layer for processed emails using primary database."""

from __future__ import annotations

from typing import Dict, Iterable, List

from db import load_recent_processed, store_processed_email_snapshot
from services.email_processor import ProcessedEmail


def initialize_cache() -> None:
    # No-op: main database is initialized elsewhere.
    return None


def store_emails(categorized: Dict[str, Iterable[ProcessedEmail]]) -> None:
    for emails in categorized.values():
        for email in emails:
            store_processed_email_snapshot(email)


def fetch_emails(limit_per_category: int = 3) -> Dict[str, List[ProcessedEmail]]:
    return load_recent_processed(limit_per_category)
