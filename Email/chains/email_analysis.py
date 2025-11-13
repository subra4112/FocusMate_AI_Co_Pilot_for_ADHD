"""LangChain chain for structured email analysis using OpenAI."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.json import parse_json_markdown
from pydantic import BaseModel, Field

from config import OPENAI_MODEL, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


class Meeting(BaseModel):
    has_meeting: bool = False
    start_iso: Optional[str] = None
    end_iso: Optional[str] = None
    location: Optional[str] = None


class Deadline(BaseModel):
    has_deadline: bool = False
    due_iso: Optional[str] = None


class EmailAnalysis(BaseModel):
    category: str = Field(description="task|instruction|meeting|deadline|marketing|info|other")
    title: Optional[str] = None
    summary: Optional[str] = None
    is_task: bool = False
    priority_hint: Optional[str] = Field(default=None, description="low|medium|high")
    steps: List[str] = Field(default_factory=list)
    meeting: Meeting = Meeting()
    deadline: Deadline = Deadline()


@dataclass
class EmailAnalysisChain:
    llm_chain: Any
    parser: PydanticOutputParser

    def invoke(self, *, subject: str, sender: str, body: str, memories: str) -> EmailAnalysis:
        payload = {
            "memories": memories,
            "subject": subject,
            "sender": sender,
            "body": body[:20000],
        }
        result = self.llm_chain.invoke(payload)
        text = self._extract_text(result)
        if not text or not str(text).strip():
            logger.error("Email analysis LLM returned empty response for subject '%s'", subject)
            raise ValueError("Email analysis model returned empty response")
        logger.debug("Email analysis raw output for subject '%s': %s", subject, text)
        try:
            return self.parser.parse(text)
        except Exception:
            logger.error("Email analysis parser fallback for subject '%s'. Raw output: %r", subject, text)
            try:
                cleaned = text.strip()
                if "{" in cleaned and "}" in cleaned:
                    start = cleaned.find("{")
                    end = cleaned.rfind("}")
                    cleaned = cleaned[start : end + 1]
                parsed = parse_json_markdown(cleaned)
                return EmailAnalysis.model_validate(parsed)
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.error("Failed to parse email analysis output: %s", exc)
                raise

    @staticmethod
    def _extract_text(result: Any) -> str:
        if isinstance(result, str):
            return result
        content = getattr(result, "content", result)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                else:
                    text = getattr(part, "text", None)
                    if text:
                        parts.append(text)
            return "".join(parts)
        return str(content)


SYSTEM_PROMPT = """You convert emails into strict JSON for an ADHD productivity app.
Decide the classification BEFORE you populate the fields. Follow this strict ordering of checks:
1. If the email requests the recipient to do something, confirm availability, attend a meeting, deliver work, or respond by a deadline/date/time → classification = "task".
   - Populate `deadline.due_iso` when a due date or specific time is mentioned.
   - Populate `meeting` fields if a meeting time window is provided.
   - Set `is_task = true`.
2. Else if the email teaches a procedure, includes numbered/bulleted steps, recipes, setup guides, or troubleshooting instructions → classification = "instruction".
   - Extract each actionable step into the `steps` array in the order presented.
3. Else → classification = "article".
   - These are newsletters, announcements, marketing updates, inspirational stories, or informational content without obligations.
Never label something as "article" if it fit the task or instruction rules above.
Keep summaries concise (<= 2 sentences) and focused on why the recipient should care.
Use prior MEMORIES when helpful. Return only the JSON that matches the schema.
Schema:
{{ schema }}
MEMORIES (optional, may be empty):
{{ memories }}
"""

HUMAN_PROMPT = """Subject: {subject}
From: {sender}
Body:
{body}
"""


def build_email_analysis_chain() -> EmailAnalysisChain:
    parser = PydanticOutputParser(pydantic_object=EmailAnalysis)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ], template_format="jinja2").partial(schema=parser.get_format_instructions())
    model = ChatOpenAI(model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
    llm_chain = prompt | model
    return EmailAnalysisChain(llm_chain=llm_chain, parser=parser)
