"""FastAPI server for the FocusMate mail assistant."""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import DEFAULT_UNREAD_WINDOW_DAYS
from db import initialize_database
from services.email_processor import EmailProcessor, ProcessedEmail, process_messages
from services.email_search import run_email_search
from tools import GmailClient, build_query, list_message_ids
from tools.calendar_client import CalendarClient
from api.cache import initialize_cache, store_emails, fetch_emails
from memory.supermemory_client import log_chat_memory

load_dotenv()

app = FastAPI(title="FocusMate Mail API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()
initialize_cache()
_processor = EmailProcessor()
_client: GmailClient = _processor.gmail
_calendar_client: Optional[CalendarClient] = None

def _get_calendar_client() -> CalendarClient:
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = CalendarClient()
    return _calendar_client


# Timeline path - assumes Plan directory is adjacent to Email directory
TIMELINE_PATH = Path(__file__).parent.parent.parent / "Plan" / "day_timeline.json"


def _collect_emails(
    *,
    days: int,
    include_read: bool,
    limit: int,
    extra_query: str = "",
) -> Dict[str, List[ProcessedEmail]]:
    categorized: Dict[str, List[ProcessedEmail]] = {"task": [], "article": [], "instruction": []}
    query = build_query(include_read=include_read, days=days, extra=extra_query)
    max_messages = limit * 6  # safeguard to avoid scanning the entire inbox

    processed_count = 0
    for message_id in list_message_ids(_client, query):
        if processed_count >= max_messages:
            break
        processed = _processor.process_message(message_id, mark_as_read=False)
        processed_count += 1
        if not processed:
            continue

        key = processed.classification
        if key not in categorized:
            continue
        if len(categorized[key]) >= limit:
            continue
        categorized[key].append(processed)

        if all(len(items) >= limit for items in categorized.values()):
            break

    return categorized


def _refresh_cache(
    *,
    days: int = DEFAULT_UNREAD_WINDOW_DAYS,
    include_read: bool = False,
    limit: int = 3,
    extra_query: str = "",
) -> Dict[str, List[ProcessedEmail]]:
    categorized = _collect_emails(
        days=days, include_read=include_read, limit=limit, extra_query=extra_query
    )
    store_emails(categorized)
    return categorized


def _get_cached(limit: int, cache_only: bool = False) -> Dict[str, List[ProcessedEmail]]:
    cached = fetch_emails(limit)
    if not cache_only and not any(len(values) for values in cached.values()):
        cached = _refresh_cache(limit=limit)
    return {key: values[:limit] for key, values in cached.items()}


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/timeline")
def get_timeline() -> dict:
    """Get the current day timeline from the Plan directory."""
    try:
        if not TIMELINE_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Timeline not found. Please run Plan/plan_my_da.py first to generate the timeline."
            )
        
        with open(TIMELINE_PATH, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
        
        return timeline
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Error parsing timeline JSON"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading timeline: {str(e)}"
        )


@app.post("/timeline/{task_id}/complete")
def mark_task_complete(task_id: str) -> dict:
    """Mark a task as complete (placeholder - extend as needed)."""
    return {
        "status": "success",
        "task_id": task_id,
        "completed": True
    }


@app.get("/calendar/events")
def get_calendar_events(
    time_min: Optional[str] = Query(None, description="ISO 8601 start time (e.g., 2025-11-01T00:00:00Z)"),
    time_max: Optional[str] = Query(None, description="ISO 8601 end time"),
    max_results: int = Query(50, ge=1, le=250),
) -> Dict[str, List[dict]]:
    """Fetch events from Google Calendar."""
    try:
        calendar = _get_calendar_client()
        events = calendar.list_events(
            max_results=max_results,
            time_min=time_min,
            time_max=time_max,
        )
        
        # Normalize events to match frontend expectations
        normalized = []
        for event in events:
            start = event.get("start", {})
            end = event.get("end", {})
            normalized.append({
                "id": event.get("id"),
                "title": event.get("summary", "Untitled Event"),
                "description": event.get("description", ""),
                "start": start.get("dateTime") or start.get("date"),
                "end": end.get("dateTime") or end.get("date"),
                "location": event.get("location", ""),
                "category": "General",
            })
        
        return {"events": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")


@app.get("/emails")
def get_emails(
    category: Optional[str] = Query(None, description="Optional category filter: task|article|instruction"),
    limit: int = Query(3, ge=1, le=20),
    refresh: bool = Query(False, description="Force refresh from Gmail instead of using cache"),
    cache_only: bool = Query(True, description="Only use cached data, never fetch from Gmail"),
) -> Dict[str, List[dict]]:
    try:
        if refresh and not cache_only:
            categorized_processed = _refresh_cache(limit=limit)
        else:
            categorized_processed = _get_cached(limit, cache_only=cache_only)
        
        categorized: Dict[str, List[dict]] = {
            key: [item.to_dict() for item in categorized_processed[key]] for key in categorized_processed
        }

        if category:
            category = category.lower()
            if category not in categorized:
                raise HTTPException(status_code=400, detail="Unsupported category")
            return {category: categorized[category]}

        return categorized
    except Exception as e:
        import traceback
        error_details = f"Failed to load emails: {str(e)}\n{traceback.format_exc()}"
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Failed to load emails: {str(e)}")


@app.post("/emails/process")
def trigger_processing(
    days: int = Query(DEFAULT_UNREAD_WINDOW_DAYS, ge=1, le=365),
    include_read: bool = Query(False),
    limit: int = Query(10, ge=1, le=50),
    extra_query: str = Query(""),
) -> Dict[str, int]:
    try:
        categorized = _refresh_cache(
            days=days, include_read=include_read, limit=limit, extra_query=extra_query
        )
        summary: Dict[str, int] = {key: len(value) for key, value in categorized.items()}
        return summary
    except Exception as e:
        import traceback
        error_details = f"Failed to process emails: {str(e)}\n{traceback.format_exc()}"
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Failed to process emails: {str(e)}")


@app.post("/emails/refresh")
def refresh_emails(
    days: int = Query(DEFAULT_UNREAD_WINDOW_DAYS, ge=1, le=365),
    include_read: bool = Query(False),
    limit: int = Query(3, ge=1, le=20),
    extra_query: str = Query(""),
) -> Dict[str, int]:
    try:
        categorized = _refresh_cache(
            days=days, include_read=include_read, limit=limit, extra_query=extra_query
        )
        return {key: len(value) for key, value in categorized.items()}
    except Exception as e:
        import traceback
        error_details = f"Failed to refresh emails: {str(e)}\n{traceback.format_exc()}"
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Failed to refresh emails: {str(e)}")


class SearchRequest(BaseModel):
    query: str
    limit: int = 12


@app.post("/emails/search")
def search_emails(body: SearchRequest):
    result = run_email_search(body.query, limit=body.limit)
    return result.model_dump()


class QAHistoryItem(BaseModel):
    role: str
    message: str


class QARequest(BaseModel):
    question: str
    limit: int = 12
    history: List[QAHistoryItem] = []
    user_id: Optional[str] = None


class QAResponse(BaseModel):
    answer: str
    follow_up_question: Optional[str] = None
    referenced_messages: List[str] = []


@app.post("/qa", response_model=QAResponse)
def follow_up_chat(body: QARequest) -> QAResponse:
    cached = fetch_emails(body.limit)
    if not any(len(values) for values in cached.values()):
        cached = _refresh_cache(limit=body.limit, include_read=True)
    history_snippets: List[str] = []
    for item in body.history[-6:]:
        role = item.role.strip().lower()
        if role not in {"user", "assistant"}:
            continue
        message = item.message.strip()
        if not message:
            continue
        history_snippets.append(f"{role.upper()}: {message}")
    normalized_question = body.question.strip()
    if not normalized_question:
        normalized_question = (
            "Provide a concise status summary of the most recent emails, including urgent tasks, "
            "noteworthy articles, and any calendar events that were scheduled."
        )
    composite_query = normalized_question
    if history_snippets:
        composite_query = "\n".join(history_snippets + [f"USER: {normalized_question}"])
    result = run_email_search(composite_query, limit=max(1, min(body.limit, 24)))
    answer = result.answer.strip() if result.answer else ""
    lower_answer = answer.lower()
    needs_fallback = (
        not answer
        or "provide more details" in lower_answer
        or "clarify" in lower_answer
        or "specific query" in lower_answer
    )
    references = result.referenced_messages

    summary_text, summary_refs = _build_structured_summary(cached, question=normalized_question)

    if needs_fallback:
        answer = summary_text
        references = summary_refs
        result.follow_up_question = None
    else:
        answer = f"{answer}\n\nInbox snapshot:\n{summary_text}"
        for ref in summary_refs:
            if ref not in references:
                references.append(ref)

    response = QAResponse(
        answer=answer,
        follow_up_question=result.follow_up_question,
        referenced_messages=references,
    )
    user_id = body.user_id or os.getenv("SUPERMEMORY_USER_ID") or "focusmate-user"
    try:
        log_chat_memory(
            user_id=user_id,
            question=normalized_question,
            answer=answer,
            references=references,
            follow_up=response.follow_up_question,
        )
    except Exception as exc:
        # Logging only; chat should continue even if memory logging fails
        logging.getLogger(__name__).debug("Supermemory chat logging failed: %s", exc)

    return response


def _build_structured_summary(
    cached: Dict[str, List[ProcessedEmail]],
    *,
    question: Optional[str] = None,
) -> Tuple[str, List[str]]:
    sections: List[str] = []
    references: List[str] = []
    focus_lines: List[str] = []

    normalized_question = (question or "").lower()

    tasks = cached.get("task", [])
    meetings = []
    deadline_tasks = []
    for email in tasks:
        note_blob = " ".join(email.notes or []).lower()
        if "calendar event created" in note_blob or "meeting" in note_blob:
            meetings.append(email)
        if "deadline" in note_blob or "due" in note_blob:
            deadline_tasks.append(email)

    if "meeting" in normalized_question or "calendar" in normalized_question:
        if meetings:
            meeting_titles = [f"{email.subject} ({email.priority_bucket.lower()})" for email in meetings[:3]]
            focus_lines.append("- **Meeting watch:** " + "; ".join(meeting_titles))
            references.extend(email.message_id for email in meetings[:3])
        else:
            focus_lines.append("- **Meeting watch:** No meetings scheduled or flagged as urgent.")

    if "deadline" in normalized_question or "due" in normalized_question:
        if deadline_tasks:
            due_titles = [f"{email.subject} ({email.priority_bucket.lower()})" for email in deadline_tasks[:3]]
            focus_lines.append("- **Deadlines:** " + "; ".join(due_titles))
            references.extend(email.message_id for email in deadline_tasks[:3])
        else:
            focus_lines.append("- **Deadlines:** No deadlines detected in the latest emails.")

    if not focus_lines and normalized_question:
        focus_lines.append(f"- **Question focus:** {question}")

    if tasks:
        top_tasks = tasks[:3]
        task_lines = [
            f"{email.subject} ({email.priority_bucket}, score {email.priority_score})"
            for email in top_tasks
        ]
        sections.append("- **Urgent tasks:** " + "; ".join(task_lines))
        references.extend(email.message_id for email in top_tasks)
    else:
        sections.append("- **Urgent tasks:** None detected.")

    articles = cached.get("article", [])
    if articles:
        top_articles = articles[:3]
        article_titles = [email.subject for email in top_articles]
        sections.append("- **Articles to scan:** " + "; ".join(article_titles))
        references.extend(email.message_id for email in top_articles)
    else:
        sections.append("- **Articles to scan:** None highlighted.")

    instructions = cached.get("instruction", [])
    if instructions:
        top_instructions = instructions[:2]
        instruction_titles = [email.subject for email in top_instructions]
        sections.append("- **Instructional steps:** " + "; ".join(instruction_titles))
        references.extend(email.message_id for email in top_instructions)
    else:
        sections.append("- **Instructional steps:** None pending.")

    combined = "\n".join(focus_lines + sections)
    return combined, references[:6]
