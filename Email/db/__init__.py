"""Database helpers for FocusMate."""

from .storage import (
    initialize_database,
    email_exists,
    upsert_email,
    insert_task,
    upsert_calendar_sync,
    store_processed_email_snapshot,
    load_recent_processed,
    search_processed_emails,
)

__all__ = [
    "initialize_database",
    "email_exists",
    "upsert_email",
    "insert_task",
    "upsert_calendar_sync",
    "store_processed_email_snapshot",
    "load_recent_processed",
    "search_processed_emails",
]
