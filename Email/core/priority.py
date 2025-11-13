"""Priority scoring and decision logic for FocusMate."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Literal, Optional

from dateutil import parser as dtparser
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from config import OPENAI_MODEL, OPENAI_TEMPERATURE

VIP_KEYWORDS = ["@yourcompany.com", "ceo@", "manager@"]


@dataclass
class PriorityContext:
    subject: str
    sender: str
    category: str
    summary: str
    is_task: bool
    steps: List[str]
    priority_hint: Optional[str]
    has_deadline: bool
    due_iso: Optional[str]
    due_days: Optional[int]
    vip_sender: bool
    meeting: dict


class PriorityDecision(BaseModel):
    bucket: Literal["Urgent", "Important", "Not important"]
    score: int = Field(ge=0, le=100)
    reasoning: str = Field(description="Short explanation tying the decision to the provided context.")


SYSTEM_PROMPT = """You are the prioritization agent inside an ADHD productivity assistant.
Think step-by-step about urgency, deadlines, sender importance, and workload impact.
Return ONLY the JSON matching the schema below.

Guidance:
- Use "Urgent" for time-critical or executive-level requests, imminent deadlines, or severe consequences.
- Use "Important" for meaningful work that requires attention soon but is not on fire.
- Use "Not important" for low-value, marketing, FYI, or deferred items.
- Always provide a score between 0-100 (0 lowest, 100 highest urgency) aligned with the bucket.
- Reference the context in your reasoning.

Schema:
{schema}
"""

HUMAN_PROMPT = """Email context:
{context_json}
"""


class PriorityAgent:
    def __init__(self) -> None:
        self._parser = PydanticOutputParser(pydantic_object=PriorityDecision)
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ]
        )
        self._model = ChatOpenAI(model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
        self._chain = self._prompt | self._model | self._parser

    def decide(self, context: PriorityContext) -> PriorityDecision:
        context_json = json.dumps(asdict(context), ensure_ascii=False, indent=2)
        payload = {
            "schema": self._parser.get_format_instructions(),
            "context_json": context_json,
        }
        try:
            return self._chain.invoke(payload)
        except Exception as exc:  # pragma: no cover - defensive fallback
            bucket, score = heuristic_priority(context)
            return PriorityDecision(
                bucket=bucket,
                score=score,
                reasoning=f"Fallback heuristic due to error: {exc}",
            )


def build_priority_agent() -> PriorityAgent:
    return PriorityAgent()


def heuristic_priority(context: PriorityContext) -> tuple[str, int]:
    score = priority_score(
        context.category,
        context.has_deadline,
        context.due_days,
        context.vip_sender,
    )
    return priority_bucket(score), score


def days_until(iso_timestamp: Optional[str]) -> Optional[int]:
    if not iso_timestamp:
        return None
    try:
        target = dtparser.parse(iso_timestamp)
        delta = target - datetime.utcnow()
        return int(delta.total_seconds() // 86400)
    except Exception:
        return None


def is_vip(sender: str) -> bool:
    lowered = sender.lower()
    return any(keyword in lowered for keyword in VIP_KEYWORDS)


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def priority_score(
    category: str,
    has_deadline: bool,
    due_days: Optional[int],
    vip: bool,
) -> int:
    score = 0
    if category in {"task", "meeting", "deadline", "instruction"}:
        score += 30
    if has_deadline:
        score += 25
    if vip:
        score += 15
    if due_days is not None:
        if due_days <= 1:
            score += 25
        elif due_days <= 3:
            score += 15
        elif due_days <= 7:
            score += 8
    if category == "marketing":
        score -= 30
    return _clamp(score, 0, 100)


def priority_bucket(score: int) -> str:
    if score >= 70:
        return "Urgent"
    if score >= 40:
        return "Important"
    return "Not important"
