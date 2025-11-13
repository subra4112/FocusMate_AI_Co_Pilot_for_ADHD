"""SQLite persistence layer for FocusMate."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import DB_PATH


@dataclass
class EmailRecord:
    gmail_id: str
    subject: str
    sender: str
    category: str
    summary: str
    priority_bucket: str
    raw_json: str
    created_at: datetime


@dataclass
class TaskRecord:
    email_gmail_id: str
    title: str
    due_iso: Optional[str]
    priority: str
    steps_json: str
    created_at: datetime


@dataclass
class CalendarSyncRecord:
    email_gmail_id: str
    event_id: str
    created_at: datetime


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def initialize_database() -> None:
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS EmailItem(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail_id TEXT UNIQUE,
            subject TEXT,
            sender TEXT,
            category TEXT,
            summary TEXT,
            priority_bucket TEXT,
            raw_json TEXT,
            created_at TEXT
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS Task(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_gmail_id TEXT,
            title TEXT,
            due_iso TEXT,
            priority TEXT,
            steps_json TEXT,
            created_at TEXT
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS CalendarSync(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_gmail_id TEXT UNIQUE,
            event_id TEXT,
            created_at TEXT
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS ProcessedEmailSnapshot(
            message_id TEXT PRIMARY KEY,
            category TEXT,
            subject TEXT,
            sender TEXT,
            priority_bucket TEXT,
            priority_score INTEGER,
            priority_reasoning TEXT,
            summary TEXT,
            notes_json TEXT,
            theme_image TEXT,
            flowchart TEXT,
            payload TEXT,
            cached_at TEXT
        )"""
        )
        con.commit()


def email_exists(gmail_id: str) -> bool:
    with _connect() as con:
        cur = con.cursor()
        cur.execute("SELECT 1 FROM EmailItem WHERE gmail_id=?", (gmail_id,))
        return cur.fetchone() is not None


def upsert_email(
    gmail_id: str,
    subject: str,
    sender: str,
    category: str,
    summary: str,
    priority_bucket: str,
    raw_json: str,
) -> None:
    payload = (
        gmail_id,
        subject,
        sender,
        category,
        summary,
        priority_bucket,
        raw_json,
        datetime.utcnow().isoformat(),
    )
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """INSERT OR IGNORE INTO EmailItem(
            gmail_id, subject, sender, category, summary, priority_bucket, raw_json, created_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
            payload,
        )
        con.commit()


def insert_task(
    email_gmail_id: str,
    title: str,
    due_iso: Optional[str],
    priority: str,
    steps_json: str,
) -> None:
    payload = (
        email_gmail_id,
        title,
        due_iso,
        priority,
        steps_json,
        datetime.utcnow().isoformat(),
    )
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """INSERT INTO Task(
            email_gmail_id, title, due_iso, priority, steps_json, created_at
        ) VALUES(?,?,?,?,?,?)""",
            payload,
        )
        con.commit()


def upsert_calendar_sync(email_gmail_id: str, event_id: str) -> None:
    payload = (email_gmail_id, event_id, datetime.utcnow().isoformat())
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO CalendarSync(
            email_gmail_id, event_id, created_at
        ) VALUES(?,?,?)""",
            payload,
        )
        con.commit()


def store_processed_email_snapshot(email) -> None:
    from services.email_processor import ProcessedEmail

    if not isinstance(email, ProcessedEmail):
        raise TypeError("store_processed_email_snapshot expects a ProcessedEmail instance")

    payload = (
        email.message_id,
        email.classification,
        email.subject,
        email.sender,
        email.priority_bucket,
        email.priority_score,
        email.priority_reasoning,
        email.summary or "",
        json.dumps(email.notes, ensure_ascii=False),
        email.theme_image,
        email.flowchart,
        email.to_json(),
        datetime.utcnow().isoformat(),
    )
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO ProcessedEmailSnapshot(
            message_id, category, subject, sender, priority_bucket, priority_score,
            priority_reasoning, summary, notes_json, theme_image, flowchart, payload, cached_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            payload,
        )
        con.commit()


def load_recent_processed(limit_per_category: int) -> Dict[str, List["ProcessedEmail"]]:
    from services.email_processor import ProcessedEmail

    categories = ["task", "article", "instruction"]
    result: Dict[str, List[ProcessedEmail]] = {category: [] for category in categories}
    with _connect() as con:
        cur = con.cursor()
        for category in categories:
            cur.execute(
                """SELECT payload FROM ProcessedEmailSnapshot
                WHERE category=?
                ORDER BY cached_at DESC
                LIMIT ?""",
                (category, limit_per_category),
            )
            rows = cur.fetchall()
            result[category] = [ProcessedEmail.from_json(row[0]) for row in rows]
    return result


def search_processed_emails(query: str, limit: int = 10) -> List["ProcessedEmail"]:
    from services.email_processor import ProcessedEmail

    pattern = f"%{query.lower()}%"
    with _connect() as con:
        cur = con.cursor()
        cur.execute(
            """SELECT payload FROM ProcessedEmailSnapshot
            WHERE LOWER(subject) LIKE ?
               OR LOWER(summary) LIKE ?
               OR LOWER(notes_json) LIKE ?
            ORDER BY cached_at DESC
            LIMIT ?""",
            (pattern, pattern, pattern, limit),
        )
        rows = cur.fetchall()
        return [ProcessedEmail.from_json(row[0]) for row in rows]
