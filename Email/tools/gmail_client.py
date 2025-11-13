"""Gmail helper utilities."""

from __future__ import annotations

import os
from typing import Generator, Iterable, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import GMAIL_SCOPES


class GmailClient:
    """Thin wrapper around the Gmail API."""

    def __init__(self, token_file: str = "token.json") -> None:
        self._token_file = token_file
        self._service = None

    @property
    def service(self):
        if self._service is None:
            self._service = build("gmail", "v1", credentials=self._load_credentials())
        return self._service

    def get_message(self, message_id: str, *, fmt: str = "full") -> dict:
        return self.service.users().messages().get(userId="me", id=message_id, format=fmt).execute()

    def modify_message(self, message_id: str, body: dict) -> None:
        self.service.users().messages().modify(userId="me", id=message_id, body=body).execute()

    def list_messages(
        self,
        query: str,
        *,
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterable[dict]:
        user = "me"
        page_token: Optional[str] = None
        yielded = 0
        while True:
            response = (
                self.service.users()
                .messages()
                .list(userId=user, q=query, maxResults=page_size, pageToken=page_token)
                .execute()
            )
            for message in response.get("messages", []) or []:
                if limit is not None and yielded >= limit:
                    return
                yield message
                yielded += 1
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    def _load_credentials(self) -> Credentials:
        if not os.path.exists(self._token_file):
            raise RuntimeError("Missing token.json. Run OAuth to create it.")
        creds = Credentials.from_authorized_user_file(self._token_file, GMAIL_SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
        raise RuntimeError("Invalid Google credentials; re-run OAuth.")


def build_query(
    include_read: bool = True,
    days: Optional[int] = None,
    extra: str = "",
    *,
    primary_only: bool = True,
) -> str:
    parts = ["in:inbox"]
    if primary_only:
        parts.append("category:primary")
    # include_read is retained for API compatibility but currently ignored to fetch all messages
    if days:
        parts.append(f"newer_than:{int(days)}d")
    if extra:
        parts.append(extra.strip())
    return " ".join(parts)


def list_message_ids(
    client: GmailClient,
    query: str,
    *,
    page_size: int = 100,
    limit: Optional[int] = None,
) -> Generator[str, None, None]:
    for message in client.list_messages(query, page_size=page_size, limit=limit):
        yield message["id"]
