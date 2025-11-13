"""Email search assistant built on cached snapshots."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from config import OPENAI_MODEL, OPENAI_TEMPERATURE
from db import insert_task, load_recent_processed, search_processed_emails
from tools.calendar_client import CalendarClient
from services.email_processor import ProcessedEmail


class EmailSearchOutput(BaseModel):
    answer: str = Field(description="Direct answer to the user's query using email context.")
    follow_up_question: str | None = Field(
        default=None, description="If more information is needed, ask the user a clarifying question."
    )
    referenced_messages: List[str] = Field(
        default_factory=list,
        description="List of gmail message IDs referenced when forming the answer.",
    )
    create_calendar_event: bool = False
    calendar_title: str | None = None
    calendar_start_iso: str | None = None
    calendar_end_iso: str | None = None
    cancel_calendar_event: bool = False
    cancel_calendar_event_id: str | None = None
    create_task: bool = False
    task_title: str | None = None
    task_due_iso: str | None = None


SYSTEM_PROMPT = """You are FocusMate's mail assistant. Answer the user's query using the provided email context.

EMAIL CONTEXT is provided as a JSON object with category summaries and detailed email entries.
Guidelines:
- Always attempt a best-effort answer referencing the provided emails and category summaries. If the user request is vague, offer a brief status overview highlighting urgent tasks, notable articles, and instructions.
- Only ask a short follow-up question if absolutely necessary (for example, the user gave an empty message).
- Only propose scheduling, cancellation, or task creation when the user clearly asks for it.
- The user benefits from ADHD-friendly summaries: keep responses short, structured, and calm.
  * Lead with a one-sentence headline answer.
  * Use short paragraphs, bullet points, or numbered lists.
  * Highlight any “next best action” explicitly.
  * Mention calendar or task outcomes clearly.
  * Keep tone encouraging and supportive.
- If referencing an email, mention its subject in natural language.
- When scheduling, always include start and end ISO timestamps. If the user does not supply them, ask for them instead of guessing.
Return JSON matching the schema below.
{{ format_instructions }}
"""

HUMAN_PROMPT = """User question: {query}

EMAIL CONTEXT:
{context}
"""


class EmailSearchAgent:
    def __init__(self) -> None:
        self.parser = PydanticOutputParser(pydantic_object=EmailSearchOutput)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ],
            template_format="jinja2",
        ).partial(format_instructions=self.parser.get_format_instructions())
        self.model = ChatOpenAI(model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
        self.prompt_chain = prompt | self.model
        self.calendar = CalendarClient()

    def _build_context(self, query: str, limit: int) -> Tuple[str, List[str]]:
        aggregated = load_recent_processed(limit)
        matches = search_processed_emails(query, limit=limit)
        seen_ids: set[str] = set()
        prioritized: List[ProcessedEmail] = []

        def append_email(email: ProcessedEmail) -> None:
            if email.message_id in seen_ids:
                return
            seen_ids.add(email.message_id)
            prioritized.append(email)

        for email in matches:
            append_email(email)
        for emails in aggregated.values():
            for email in emails:
                append_email(email)

        def serialize_email(email: ProcessedEmail) -> Dict[str, Any]:
            summary = email.summary or next(
                (
                    note.replace("ADHD-friendly summary: ", "")
                    for note in email.notes
                    if note.lower().startswith("adhd-friendly summary")
                ),
                "",
            )
            return {
                "message_id": email.message_id,
                "category": email.classification,
                "subject": email.subject,
                "sender": email.sender,
                "priority_bucket": email.priority_bucket,
                "priority_score": email.priority_score,
                "summary": summary,
                "notes": email.notes,
                "theme_image": email.theme_image,
                "flowchart": email.flowchart,
                "calendar_event_link": email.calendar_event_link,
            }

        category_summary = {category: len(emails) for category, emails in aggregated.items()}
        categories_payload = {
            category: [serialize_email(email) for email in emails[:limit]]
            for category, emails in aggregated.items()
        }
        prioritized_payload = [serialize_email(email) for email in prioritized[:limit]]
        message_ids = [email["message_id"] for email in prioritized_payload]
        if not message_ids:
            for emails in aggregated.values():
                for email in emails[: min(3, len(emails))]:
                    if email.message_id not in message_ids:
                        message_ids.append(email.message_id)

        context_payload = {
            "category_summary": category_summary,
            "categories": categories_payload,
            "matches": prioritized_payload,
            "user_query_hint": query,
        }

        context = json.dumps(context_payload, ensure_ascii=False)
        return context, message_ids

    def search(self, query: str, *, limit: int = 12) -> EmailSearchOutput:
        context, candidate_ids = self._build_context(query, limit)
        response = self.prompt_chain.invoke({"query": query, "context": context})
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)

        try:
            output = self.parser.parse(text)
        except (ValueError, TypeError):
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                cleaned = text[start : end + 1]
                output = self.parser.parse(cleaned)
            else:
                raise

        if not output.referenced_messages:
            output.referenced_messages = candidate_ids[:3]
        self._maybe_execute_actions(output)
        return output

    def _maybe_execute_actions(self, output: EmailSearchOutput) -> None:
        if output.create_calendar_event and output.calendar_title and output.calendar_start_iso and output.calendar_end_iso:
            try:
                event_data = self.calendar.create_event(
                    output.calendar_title,
                    output.calendar_start_iso,
                    output.calendar_end_iso,
                )
                event_id = event_data.get("id") if isinstance(event_data, dict) else event_data
                event_link = event_data.get("htmlLink") if isinstance(event_data, dict) else None
                link_text = f" (link: {event_link})" if event_link else ""
                output.answer += f"\n\n✅ Scheduled '{output.calendar_title}' (event id: {event_id}).{link_text}"
            except Exception as exc:  # pragma: no cover - calendaring is best-effort
                output.answer += f"\n\n⚠️ Calendar scheduling failed: {exc}."
        elif output.create_calendar_event:
            if not output.follow_up_question:
                output.follow_up_question = "Could you share the start and end time for the event so I can schedule it?"
        elif output.cancel_calendar_event and output.cancel_calendar_event_id:
            try:
                self.calendar.delete_event(output.cancel_calendar_event_id)
                output.answer += f"\n\n🗑️ Cancelled calendar event {output.cancel_calendar_event_id}."
            except Exception as exc:  # pragma: no cover - calendar deletion is best-effort
                output.answer += f"\n\n⚠️ Failed to cancel calendar event: {exc}."

        if output.create_task and output.task_title:
            task_id = f"search-task-{uuid.uuid4().hex[:8]}"
            insert_task(
                task_id,
                output.task_title,
                output.task_due_iso,
                "medium",
                json.dumps([output.answer], ensure_ascii=False),
            )
            output.answer += f"\n\n📝 Added task '{output.task_title}'."
        elif output.create_task and not output.follow_up_question:
            output.follow_up_question = "What title and deadline should I use for the task?"


def run_email_search(query: str, limit: int = 12) -> EmailSearchOutput:
    agent = EmailSearchAgent()
    return agent.search(query, limit=limit)
