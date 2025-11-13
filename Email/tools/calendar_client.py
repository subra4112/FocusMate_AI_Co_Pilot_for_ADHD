"""Google Calendar helper utilities."""

from __future__ import annotations

import os
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import CALENDAR_SCOPES


class CalendarClient:
    def __init__(self, token_file: str = "token.json") -> None:
        self._token_file = token_file
        self._service = None

    @property
    def service(self):
        if self._service is None:
            credentials = self._load_credentials()
            self._service = build("calendar", "v3", credentials=credentials)
        return self._service

    def create_event(
        self,
        title: str,
        start_iso: str,
        end_iso: str,
        *,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> dict[str, Optional[str]]:
        event_body = {
            "summary": title,
            "location": location or None,
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso},
        }
        event = self.service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return {
            "id": event.get("id"),
            "htmlLink": event.get("htmlLink"),
        }

    def delete_event(self, event_id: str, *, calendar_id: str = "primary") -> None:
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def list_events(
        self,
        *,
        calendar_id: str = "primary",
        max_results: int = 50,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
    ) -> list[dict]:
        """Fetch events from Google Calendar within the given time range."""
        params = {
            "calendarId": calendar_id,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        events_result = self.service.events().list(**params).execute()
        return events_result.get("items", [])

    def _load_credentials(self) -> Credentials:
        if not os.path.exists(self._token_file):
            raise RuntimeError("Missing token.json. Run OAuth to create it.")
        creds = Credentials.from_authorized_user_file(self._token_file, CALENDAR_SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
        raise RuntimeError("Invalid Google credentials; re-run OAuth.")


def create_deadline_hold(calendar: CalendarClient, title: str, due_iso: str) -> dict[str, Optional[str]]:
    start = f"{due_iso}T09:00:00"
    end = f"{due_iso}T09:30:00"
    return calendar.create_event(f"{title} (deadline)", start, end)
