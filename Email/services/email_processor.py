"""Email processing workflow for FocusMate."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Tuple

from dotenv import load_dotenv
from chains import EmailAnalysis, EmailAnalysisChain, build_email_analysis_chain
from core.priority import (
    PriorityAgent,
    PriorityContext,
    build_priority_agent,
    days_until,
    is_vip,
)
from db import email_exists, insert_task, store_processed_email_snapshot, upsert_calendar_sync, upsert_email
from tools import (
    CalendarClient,
    GmailClient,
    create_deadline_hold,
    decode_body,
    generate_logo_dalle,
    header,
    html_to_text,
)
from langchain_openai import ChatOpenAI
from config import OPENAI_MODEL, OPENAI_TEMPERATURE
from dateutil import parser as date_parser
from dateutil import tz


load_dotenv()

TASK_CATEGORIES = {"task", "deadline", "meeting"}
INSTRUCTION_CATEGORIES = {"instruction"}
TASK_KEYWORDS = {
    "deadline",
    "due",
    "submit",
    "delivery",
    "deliverable",
    "confirm",
    "availability",
    "rsvp",
    "schedule",
    "interview",
    "meeting",
    "appointment",
    "respond",
    "reply",
}
DEADLINE_KEYWORDS = {"deadline", "due", "due date", "by eod", "by end of day", "before", "no later than"}
INSTRUCTION_KEYWORDS = {"instructions", "steps", "step-by-step", "method", "how to", "setup", "troubleshooting", "recipe"}
STEP_PATTERN = re.compile(r"^\s*(?:step\s*\d+[:.)-]?|[\d]+\s*[.)-]|[-*•])\s+(.*)", re.IGNORECASE)
TZ_ALIASES = {
    "UTC": "UTC",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Phoenix",
    "MDT": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
}
DEFAULT_MEETING_DURATION_MINUTES = 45


THEME_IMAGES = {
    "food": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
    "finance": "https://images.unsplash.com/photo-1556740749-887f6717d7e4",
    "security": "https://images.unsplash.com/photo-1556740749-887f6717d7e4",
    "travel": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
    "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475",
    "health": "https://images.unsplash.com/photo-1514996937319-344454492b37",
}
DEFAULT_THEME_IMAGE = "https://images.unsplash.com/photo-1498050108023-c5249f4df085"
GENERATED_IMAGE_CACHE: dict[str, str] = {}

logger = logging.getLogger(__name__)


@dataclass
class ProcessedEmail:
    message_id: str
    subject: str
    sender: str
    received_at: Optional[str]
    priority_bucket: str
    priority_score: int
    priority_reasoning: str
    classification: str
    notes: List[str] = field(default_factory=list)
    theme_image: Optional[str] = None
    flowchart: Optional[str] = None
    flowchart_type: Optional[str] = None
    summary: Optional[str] = None
    calendar_event_link: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "received_at": self.received_at,
            "priority_bucket": self.priority_bucket,
            "priority_score": self.priority_score,
            "priority_reasoning": self.priority_reasoning,
            "classification": self.classification,
            "notes": self.notes,
            "theme_image": self.theme_image,
            "flowchart": self.flowchart,
            "flowchart_type": self.flowchart_type,
            "summary": self.summary,
            "calendar_event_link": self.calendar_event_link,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, payload: str) -> "ProcessedEmail":
        data = json.loads(payload)
        return cls(
            message_id=data.get("message_id", ""),
            subject=data.get("subject", ""),
            sender=data.get("sender", ""),
            received_at=data.get("received_at"),
            priority_bucket=data.get("priority_bucket", "Not important"),
            priority_score=data.get("priority_score", 0),
            priority_reasoning=data.get("priority_reasoning", ""),
            classification=data.get("classification", "article"),
            notes=data.get("notes", []),
            theme_image=data.get("theme_image"),
            flowchart=data.get("flowchart"),
            flowchart_type=data.get("flowchart_type"),
            summary=data.get("summary"),
            calendar_event_link=data.get("calendar_event_link"),
        )


class EmailProcessor:
    def __init__(
        self,
        gmail_client: Optional[GmailClient] = None,
        calendar_client: Optional[CalendarClient] = None,
        analysis_chain: Optional[EmailAnalysisChain] = None,
        priority_agent: Optional[PriorityAgent] = None,
    ) -> None:
        self.gmail = gmail_client or GmailClient()
        self.calendar = calendar_client or CalendarClient()
        self.analysis_chain = analysis_chain or build_email_analysis_chain()
        self.priority_agent = priority_agent or build_priority_agent()

    def process_message(self, message_id: str, *, mark_as_read: bool) -> Optional[ProcessedEmail]:
        message = self.gmail.get_message(message_id, fmt="full")
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        subject = header(headers, "Subject")
        sender = header(headers, "From")
        received_ms = int(message.get("internalDate", "0"))
        received_iso = datetime.utcfromtimestamp(received_ms / 1000).isoformat() + "Z"

        body_html = decode_body(payload)
        body_text = html_to_text(body_html)

        analysis: EmailAnalysis = self.analysis_chain.invoke(
            subject=subject,
            sender=sender,
            body=body_text,
            memories="",
        )

        has_deadline = analysis.deadline.has_deadline and bool(analysis.deadline.due_iso)
        due_iso = analysis.deadline.due_iso if has_deadline else None
        due_days = days_until(due_iso)
        vip = is_vip(sender)

        context = PriorityContext(
            subject=subject,
            sender=sender,
            category=analysis.category,
            summary=analysis.summary or "",
            is_task=analysis.is_task,
            steps=analysis.steps,
            priority_hint=analysis.priority_hint,
            has_deadline=has_deadline,
            due_iso=due_iso,
            due_days=due_days,
            vip_sender=vip,
            meeting=analysis.meeting.model_dump(),
        )

        decision = self.priority_agent.decide(context)
        bucket = decision.bucket
        score = decision.score

        if not email_exists(message_id):
            self._persist_email(message_id, subject, sender, bucket, analysis)

        notes: List[str] = []
        theme_image: Optional[str] = None
        flowchart: Optional[str] = None
        task_hint = detect_task_intent(subject, body_text)
        deadline_hint = detect_deadline(body_text)
        detected_deadline_iso = extract_deadline_datetime(body_text)
        if detected_deadline_iso and not analysis.deadline.due_iso:
            analysis.deadline.due_iso = detected_deadline_iso
        if analysis.deadline.due_iso:
            analysis.deadline.has_deadline = True
        instruction_steps = extract_instruction_steps(body_text)
        instruction_hint = bool(instruction_steps) or detect_instruction(body_text)
        meeting_window = extract_meeting_window(body_text)
        if meeting_window and not analysis.meeting.has_meeting:
            start_iso, end_iso = meeting_window
            analysis.meeting.has_meeting = True
            analysis.meeting.start_iso = start_iso
            analysis.meeting.end_iso = end_iso

        if instruction_hint and not analysis.steps:
            analysis.steps = instruction_steps or analysis.steps
        if task_hint:
            analysis.is_task = True
            if deadline_hint and not analysis.deadline.has_deadline:
                analysis.deadline.has_deadline = True
                if not analysis.deadline.due_iso:
                    analysis.deadline.due_iso = None
        has_deadline_flag = analysis.deadline.has_deadline and bool(analysis.deadline.due_iso)
        due_iso = analysis.deadline.due_iso if has_deadline_flag else None
        classification, event_id, event_link = self._categorize_and_act(
            message_id,
            subject,
            analysis,
            score,
            has_deadline_flag,
            due_iso,
            body_text,
            task_hint=task_hint,
            deadline_hint=deadline_hint,
            instruction_hint=instruction_hint,
        )

        flowchart: Optional[str] = None
        flowchart_type: Optional[str] = None
        if classification == "task":
            if event_id:
                notes.append(f"Acknowledgement: Calendar event created (id: {event_id}).")
                if event_link:
                    notes.append(f"Calendar link: {event_link}")
            else:
                notes.append("Acknowledgement: Task captured for follow-up (calendar unavailable).")
            notes.append(f"ADHD-friendly summary: {analysis.summary or 'Focus on the key next step and timebox it.'}")
        elif classification == "instruction":
            flowchart, flowchart_type = build_flowchart(analysis.steps, analysis.summary or subject)
            notes.append("Instruction flowchart generated for step-by-step execution.")
        else:  # article
            theme_image = select_theme_image(analysis.summary or subject)
            dall_e_image = fetch_generated_image(subject)
            if dall_e_image:
                theme_image = dall_e_image
            notes.append(
                f"ADHD-friendly summary: {analysis.summary or 'Key idea: skim the highlights and capture one actionable takeaway.'}"
            )
            if theme_image:
                notes.append(f"Theme image: {theme_image}")

        processed_email = ProcessedEmail(
            message_id=message_id,
            subject=subject,
            sender=sender,
            received_at=received_iso,
            priority_bucket=bucket,
            priority_score=score,
            priority_reasoning=decision.reasoning,
            classification=classification,
            notes=notes,
            theme_image=theme_image,
            flowchart=flowchart,
            flowchart_type=flowchart_type,
            summary=analysis.summary,
            calendar_event_link=event_link if classification == "task" else None,
        )

        store_processed_email_snapshot(processed_email)

        if mark_as_read:
            self.gmail.modify_message(message_id, {"removeLabelIds": ["UNREAD"]})

        return processed_email

    def _persist_email(
        self,
        message_id: str,
        subject: str,
        sender: str,
        bucket: str,
        analysis: EmailAnalysis,
    ) -> None:
        upsert_email(
            message_id,
            subject,
            sender,
            analysis.category,
            analysis.summary or "",
            bucket,
            analysis.model_dump_json(),
        )

    def _categorize_and_act(
        self,
        message_id: str,
        subject: str,
        analysis: EmailAnalysis,
        score: int,
        has_deadline: bool,
        due_iso: Optional[str],
        body_text: str,
        *,
        task_hint: bool,
        deadline_hint: bool,
        instruction_hint: bool,
    ) -> Tuple[str, Optional[str], Optional[str]]:
        effective_deadline = has_deadline or deadline_hint
        normalized_category = (analysis.category or "").strip().lower()

        if normalized_category in {"task", "deadline", "meeting"}:
            event_id, event_link = self._handle_task_actions(
                message_id,
                subject,
                score,
                analysis,
                effective_deadline,
                due_iso,
                force=task_hint,
            )
            return "task", event_id, event_link

        if normalized_category == "instruction":
            if not analysis.steps and instruction_hint:
                analysis.steps = extract_instruction_steps(body_text)
            return "instruction", None, None

        if normalized_category == "article":
            return "article", None, None

        # Fallback for unexpected categories: lean on hints but prefer instruction when steps exist.
        if instruction_hint and (analysis.steps or extract_instruction_steps(body_text)):
            if not analysis.steps:
                analysis.steps = extract_instruction_steps(body_text)
            return "instruction", None, None

        if task_hint or analysis.is_task or effective_deadline:
            event_id, event_link = self._handle_task_actions(
                message_id,
                subject,
                score,
                analysis,
                effective_deadline,
                due_iso,
                force=True,
            )
            return "task", event_id, event_link

        return "article", None, None

    def _handle_task_actions(
        self,
        message_id: str,
        subject: str,
        score: int,
        analysis: EmailAnalysis,
        has_deadline: bool,
        due_iso: Optional[str],
        *,
        force: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        should_track_task = force or analysis.is_task or analysis.category in TASK_CATEGORIES or has_deadline
        if should_track_task:
            priority = "high" if score >= 70 else "medium" if score >= 40 else "low"
            insert_task(
                message_id,
                analysis.title or subject,
                analysis.deadline.due_iso if has_deadline else None,
                priority,
                json.dumps(analysis.steps, ensure_ascii=False),
            )
        event_id, event_link = self._maybe_create_calendar_event(
            message_id,
            subject,
            analysis,
            has_deadline,
            due_iso,
        )
        return event_id, event_link

    def _maybe_create_calendar_event(
        self,
        message_id: str,
        subject: str,
        analysis: EmailAnalysis,
        has_deadline: bool,
        due_iso: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        event_id = None
        event_link = None
        if analysis.meeting.has_meeting and analysis.meeting.start_iso and analysis.meeting.end_iso:
            try:
                event = self.calendar.create_event(
                    analysis.title or subject,
                    analysis.meeting.start_iso,
                    analysis.meeting.end_iso,
                    location=analysis.meeting.location or None,
                )
                event_id = event.get("id")
                event_link = event.get("htmlLink")
            except Exception as exc:  # pragma: no cover - tolerant fallback
                logger.warning("Calendar event creation failed: %s", exc)
                event_id = None
        elif has_deadline and due_iso:
            try:
                event = create_deadline_hold(self.calendar, analysis.title or subject, due_iso)
                event_id = event.get("id") if isinstance(event, dict) else None
                event_link = event.get("htmlLink") if isinstance(event, dict) else None
            except Exception as exc:  # pragma: no cover - tolerant fallback
                logger.warning("Calendar deadline hold failed: %s", exc)
                event_id = None
        if event_id:
            upsert_calendar_sync(message_id, event_id)
        return event_id, event_link


def process_messages(
    message_ids: Iterable[str],
    *,
    mark_as_read: bool,
    processor: EmailProcessor,
) -> Iterable[ProcessedEmail]:
    for message_id in message_ids:
        processed = processor.process_message(message_id, mark_as_read=mark_as_read)
        if processed:
            yield processed


def select_theme_image(summary: str) -> str:
    lowered = summary.lower()
    for keyword, image_url in THEME_IMAGES.items():
        if keyword in lowered:
            return image_url
    return DEFAULT_THEME_IMAGE


def fetch_generated_image(subject: str) -> Optional[str]:
    if not subject.strip():
        return None
    key = subject.strip().lower()
    if key in GENERATED_IMAGE_CACHE:
        return GENERATED_IMAGE_CACHE[key]
    image_url = generate_logo_dalle(subject.strip())
    if image_url:
        GENERATED_IMAGE_CACHE[key] = image_url
    return image_url


def build_flowchart(steps: List[str], fallback: str) -> Tuple[str, str]:
    candidate_steps = [step.strip() for step in steps if step and step.strip()]
    if not candidate_steps:
        sentences = [segment.strip() for segment in fallback.split(".") if segment.strip()]
        if len(sentences) >= 2:
            candidate_steps = [sentence for sentence in sentences[:4]]
        elif fallback:
            candidate_steps = [fallback.strip()]
        else:
            candidate_steps = ["Follow the described instructions"]
    payload = {"steps": candidate_steps}
    return json.dumps(payload, ensure_ascii=False), "json"


def detect_task_intent(subject: str, body: str) -> bool:
    text = f"{subject}\n{body}".lower()
    return any(keyword in text for keyword in TASK_KEYWORDS)


def detect_deadline(body: str) -> bool:
    lowered = body.lower()
    return any(keyword in lowered for keyword in DEADLINE_KEYWORDS)


def detect_instruction(body: str) -> bool:
    lowered = body.lower()
    return any(keyword in lowered for keyword in INSTRUCTION_KEYWORDS)


def extract_instruction_steps(body: str, *, max_steps: int = 12) -> List[str]:
    steps: List[str] = []
    for line in body.splitlines():
        match = STEP_PATTERN.match(line)
        if match:
            step_text = match.group(1).strip()
            if step_text:
                steps.append(step_text)
        elif steps and line.strip() and not line.strip().endswith(":"):
            if len(line.strip()) <= 120:
                steps[-1] = f"{steps[-1]} {line.strip()}"
    if len(steps) >= 2:
        return steps[:max_steps]
    return []


def extract_deadline_datetime(body: str) -> Optional[str]:
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if lowered.startswith(("deadline", "due", "due date")):
            candidate = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
            dt = _parse_datetime_string(candidate)
            if dt:
                return dt.isoformat()
    return None


def extract_meeting_window(body: str) -> Optional[Tuple[str, str]]:
    date_text: Optional[str] = None
    time_text: Optional[str] = None
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if lowered.startswith(("date:", "🗓 date:")):
            date_text = stripped.split(":", 1)[-1].strip()
        elif lowered.startswith(("time:", "🕐 time:", "🕑 time:", "🕒 time:")):
            time_text = stripped.split(":", 1)[-1].strip()
        elif lowered.startswith(("duration:", "length:")) and time_text is None:
            time_text = stripped.split(":", 1)[-1].strip()
    if not date_text or not time_text:
        return None
    start_text, end_text = _split_time_range(time_text)
    timezone_token = _extract_timezone_token(end_text or start_text)
    if timezone_token:
        if timezone_token not in start_text:
            start_text = f"{start_text} {timezone_token}"
        if end_text and timezone_token not in end_text:
            end_text = f"{end_text} {timezone_token}"
    start_dt = _parse_datetime_string(f"{date_text} {start_text}")
    if not start_dt:
        return None
    if end_text:
        end_dt = _parse_datetime_string(f"{date_text} {end_text}")
    else:
        end_dt = start_dt + timedelta(minutes=DEFAULT_MEETING_DURATION_MINUTES)
    if not end_dt or end_dt <= start_dt:
        end_dt = start_dt + timedelta(minutes=DEFAULT_MEETING_DURATION_MINUTES)
    return start_dt.isoformat(), end_dt.isoformat()


def _split_time_range(value: str) -> Tuple[str, Optional[str]]:
    clean_value = value.replace("(", "").replace(")", "")
    parts = re.split(r"\s*(?:–|—|-|to)\s*", clean_value, maxsplit=1)
    if not parts:
        return clean_value.strip(), None
    if len(parts) == 1:
        return parts[0].strip(), None
    start = parts[0].strip()
    end = parts[1].strip()
    return start, end or None


def _parse_datetime_string(text: str) -> Optional[datetime]:
    tzinfos = {abbr: tz.gettz(alias) for abbr, alias in TZ_ALIASES.items()}
    try:
        dt = date_parser.parse(text, fuzzy=True, tzinfos=tzinfos)
    except (ValueError, OverflowError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.gettz("UTC"))
    return dt


def _extract_timezone_token(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"\b([A-Z]{2,4})\b", text)
    if match:
        token = match.group(1)
        if token in TZ_ALIASES:
            return token
    return None
