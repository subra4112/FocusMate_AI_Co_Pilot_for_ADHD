"""FocusMate CLI entry point."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from dotenv import load_dotenv
from config import DEFAULT_BACKFILL_WINDOW_DAYS, DEFAULT_POLL_INTERVAL, DEFAULT_UNREAD_WINDOW_DAYS
from db import initialize_database
from services.email_processor import EmailProcessor, ProcessedEmail, process_messages
from tools import GmailClient, build_query, list_message_ids


load_dotenv()


@dataclass
class RunConfig:
    backfill_days: Optional[int] = None
    unread_days: Optional[int] = None
    poll_interval_minutes: int = DEFAULT_POLL_INTERVAL
    include_read: bool = False
    extra_query: str = ""
    summary: bool = False
    limit: int = 3


class FocusMateApp:
    def __init__(self, processor: Optional[EmailProcessor] = None) -> None:
        self.processor = processor or EmailProcessor()
        self.gmail_client = self.processor.gmail

    def run_backfill(self, days: int, *, extra_query: str = "") -> None:
        query = build_query(include_read=True, days=days, extra=extra_query)
        message_ids = list_message_ids(self.gmail_client, query, limit=10)
        for processed in process_messages(message_ids, mark_as_read=False, processor=self.processor):
            self._print_result(processed)

    def run_unread(self, days: int, *, extra_query: str = "", include_read: bool = False) -> None:
        query = build_query(include_read=include_read, days=days, extra=extra_query)
        message_ids = list_message_ids(self.gmail_client, query, limit=10)
        mark_as_read = not include_read
        for processed in process_messages(message_ids, mark_as_read=mark_as_read, processor=self.processor):
            self._print_result(processed)

    def _print_result(self, processed):
        timestamp = f" [{processed.received_at}]" if processed.received_at else ""
        print(f"[{processed.priority_bucket}] ({processed.classification.upper()}){timestamp} {processed.subject}")
        if processed.notes:
            for note in processed.notes:
                print(f"  - {note}")
        if processed.flowchart:
            print("  Flowchart (mermaid):")
            for line in processed.flowchart.splitlines():
                print(f"    {line}")
        if processed.theme_image:
            print(f"  Theme image hint: {processed.theme_image}")
        print(f"  Priority reasoning: {processed.priority_reasoning}")
        print()

    def run_polling(self, days: int, *, interval_minutes: int, extra_query: str = "") -> None:
        if interval_minutes <= 0:
            raise ValueError("Polling interval must be greater than zero minutes.")
        print(f"Starting polling every {interval_minutes} minute(s). Press Ctrl+C to stop.")
        try:
            while True:
                self.run_unread(days, extra_query=extra_query, include_read=False)
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("Polling interrupted by user.")

    def show_summary(
        self,
        limit_per_category: int,
        *,
        days: int,
        include_read: bool,
        extra_query: str = "",
    ) -> None:
        categorized = self._collect_emails(
            limit_per_category=limit_per_category,
            days=days,
            include_read=include_read,
            extra_query=extra_query,
            max_total=10,
        )
        total = sum(len(items) for items in categorized.values())
        print(f"\nSummary for last {days} day(s) (include_read={include_read}):")
        print(f"Total processed: {total}")
        for category, items in categorized.items():
            print(f"\n=== {category.upper()} ({len(items)}) ===")
            if not items:
                print("  No emails found.")
                continue
            for email in items:
                self._print_result(email)

    def _collect_emails(
        self,
        *,
        limit_per_category: int,
        days: int,
        include_read: bool,
        extra_query: str,
        max_total: int = 10,
    ) -> Dict[str, List[ProcessedEmail]]:
        categorized: Dict[str, List[ProcessedEmail]] = {"task": [], "article": [], "instruction": []}
        query = build_query(include_read=include_read, days=days, extra=extra_query)
        max_messages = min(limit_per_category * 6, max_total)
        processed_count = 0

        for message_id in list_message_ids(self.gmail_client, query, limit=max_messages):
            if processed_count >= max_messages:
                break
            processed = self.processor.process_message(message_id, mark_as_read=False)
            processed_count += 1
            if processed is None:
                continue
            bucket = processed.classification
            if bucket not in categorized:
                continue
            if len(categorized[bucket]) >= limit_per_category:
                continue
            categorized[bucket].append(processed)
            if all(len(items) >= limit_per_category for items in categorized.values()):
                break
        return categorized


def parse_args() -> RunConfig:
    parser = argparse.ArgumentParser(description="FocusMate Mail AI")
    parser.add_argument("--backfill", type=int, nargs="?", const=DEFAULT_BACKFILL_WINDOW_DAYS, help="Backfill read+unread emails for last N days")
    parser.add_argument("--unread", type=int, nargs="?", const=DEFAULT_UNREAD_WINDOW_DAYS, help="Process unread emails for last N days")
    parser.add_argument("--poll", type=int, nargs="?", const=DEFAULT_POLL_INTERVAL, help="Enable periodic polling in minutes (requires --unread)")
    parser.add_argument("--query", type=str, default="", help="Extra Gmail search filters (e.g. label:work)")
    parser.add_argument("--summary", action="store_true", help="Print categorized summary to the console without marking emails as read")
    parser.add_argument("--include-read", action="store_true", help="Include read emails when building summaries or processing unread")
    parser.add_argument("--limit", type=int, default=3, help="Emails per category to display in summary mode (default: 3)")
    args = parser.parse_args()

    return RunConfig(
        backfill_days=args.backfill,
        unread_days=args.unread,
        poll_interval_minutes=args.poll if args.poll is not None else DEFAULT_POLL_INTERVAL,
        extra_query=args.query or "",
        summary=args.summary,
        include_read=args.include_read,
        limit=max(1, args.limit),
    )


def main() -> None:
    initialize_database()
    config = parse_args()
    app = FocusMateApp()

    if config.summary:
        days = config.unread_days or DEFAULT_UNREAD_WINDOW_DAYS
        app.show_summary(
            config.limit,
            days=days,
            include_read=config.include_read,
            extra_query=config.extra_query,
        )
        return

    if config.backfill_days:
        app.run_backfill(config.backfill_days, extra_query=config.extra_query)

    if config.unread_days:
        app.run_unread(
            config.unread_days,
            extra_query=config.extra_query,
            include_read=config.include_read,
        )
        if config.poll_interval_minutes and config.poll_interval_minutes > 0:
            app.run_polling(
                config.unread_days,
                interval_minutes=config.poll_interval_minutes,
                extra_query=config.extra_query,
            )
    elif not config.backfill_days:
        app.run_unread(DEFAULT_UNREAD_WINDOW_DAYS, extra_query=config.extra_query)


if __name__ == "__main__":
    main()
