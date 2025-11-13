"""Supermemory client helpers."""

from __future__ import annotations

import hashlib
import json
import os
import logging
from typing import Any, Dict, List, Callable, Optional
from dotenv import load_dotenv
from langchain_core.retrievers import BaseRetriever
from config import SUPERMEMORY_DEFAULT_TOP_K

logger = logging.getLogger(__name__)

load_dotenv()
class SupermemoryRetriever(BaseRetriever):
    """LangChain retriever wrapper around the Supermemory search API."""

    user_id: str
    k: int = SUPERMEMORY_DEFAULT_TOP_K

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, user_id: str, *, k: int = SUPERMEMORY_DEFAULT_TOP_K):
        super().__init__(user_id=user_id, k=k)
        self._client = self._init_client()

    def _init_client(self):
        from supermemory import Supermemory  # imported lazily

        api_key = os.getenv("SUPERMEMORY_API_KEY")
        if not api_key:
            raise RuntimeError("SUPERMEMORY_API_KEY is not configured in the environment.")
        return Supermemory(api_key=api_key)

    def _search(self, query: str) -> List[Dict[str, Any]]:
        strategies: List[Callable[[], Any]] = []

        # SDK variant 1: client.search.memories(...)
        if hasattr(self._client, "search") and hasattr(self._client.search, "memories"):
            strategies.append(lambda: self._client.search.memories(user_id=self.user_id, q=query, limit=self.k))

        # SDK variant 2: client.memories.search(...)
        memories_api = getattr(self._client, "memories", None)
        if memories_api is not None:
            if hasattr(memories_api, "search"):
                strategies.append(lambda: memories_api.search(user_id=self.user_id, query=query, limit=self.k))
            if hasattr(memories_api, "query"):
                strategies.append(lambda: memories_api.query(user_id=self.user_id, query=query, limit=self.k))
            if hasattr(memories_api, "list"):
                strategies.append(lambda: memories_api.list(user_id=self.user_id, limit=self.k, q=query))

        response = None
        for call in strategies:
            try:
                response = call()
                break
            except TypeError as exc:
                logger.debug("Supermemory search TypeError, trying next strategy: %s", exc)
            except Exception as exc:
                logger.debug("Supermemory search attempt failed: %s", exc)

        if response is None:
            logger.warning("Supermemory search failed; no compatible API signature found.")
            return []

        docs: List[Dict[str, Any]] = []
        for item in getattr(response, "results", []) or []:
            text = getattr(item, "text", None) or item.get("text") if isinstance(item, dict) else None
            metadata = getattr(item, "metadata", None) or item.get("metadata") if isinstance(item, dict) else {}
            if text is None:
                continue
            docs.append({"page_content": text, "metadata": metadata})
        return docs

    def get_relevant_documents(self, query: str):
        return self._search(query)

    def _get_relevant_documents(self, query: str, *, run_manager=None):  # type: ignore[override]
        return self._search(query)

    async def _aget_relevant_documents(self, query: str, *, run_manager=None):  # type: ignore[override]
        return self._search(query)


def upsert_email_memory(
    user_id: str,
    subject: str,
    sender: str,
    thread_id: str,
    received_iso: str,
    analysis: Dict[str, Any],
    message_id: str,
) -> None:
    from supermemory import Supermemory

    api_key = os.environ.get("SUPERMEMORY_API_KEY")
    if not api_key:
        raise RuntimeError("SUPERMEMORY_API_KEY is not configured in the environment.")

    client = Supermemory(api_key=api_key)
    memory_id_input = f"{sender}|{subject}|{thread_id}"
    memory_id = "email:" + hashlib.sha256(memory_id_input.encode()).hexdigest()[:16]

    document = {
        "id": memory_id,
        "type": "email",
        "text": json.dumps(
            {
                "subject": subject,
                "summary": analysis.get("summary"),
                "steps": analysis.get("steps", []),
                "title": analysis.get("title"),
                "received_iso": received_iso,
            },
            ensure_ascii=False,
        ),
        "metadata": {
            "messageId": message_id,
            "threadId": thread_id,
            "from": sender,
            "category": analysis.get("category"),
            "priority_hint": analysis.get("priority_hint"),
            "due_iso": (analysis.get("deadline") or {}).get("due_iso"),
            "meeting": analysis.get("meeting", {}),
        },
    }

    memories_api = getattr(client, "memories", None)
    if memories_api is None:
        logger.warning("Supermemory client has no 'memories' attribute; skipping memory upsert.")
        return

    strategies: List[Callable[[], Any]] = []
    if hasattr(memories_api, "upsert"):
        strategies.append(lambda: memories_api.upsert(user_id=user_id, memories=[document]))
    if hasattr(memories_api, "add"):
        strategies.append(lambda: memories_api.add(user_id=user_id, memories=[document]))
    if hasattr(memories_api, "create"):
        strategies.append(lambda: memories_api.create(user_id=user_id, memories=[document]))

    for call in strategies:
        try:
            call()
            return
        except TypeError as exc:
            logger.debug("Supermemory memory write TypeError, trying next strategy: %s", exc)
        except Exception as exc:
            logger.debug("Supermemory memory write attempt failed: %s", exc)

    logger.warning("Supermemory memory write failed; no compatible API signature found.")


def log_chat_memory(
    user_id: str,
    question: str,
    answer: str,
    *,
    references: Optional[List[str]] = None,
    follow_up: Optional[str] = None,
) -> None:
    api_key = os.environ.get("SUPERMEMORY_API_KEY")
    if not api_key:
        logger.debug("SUPERMEMORY_API_KEY missing; skipping chat memory logging.")
        return

    from supermemory import Supermemory

    client = Supermemory(api_key=api_key)
    memories_api = getattr(client, "memories", None)
    if memories_api is None:
        logger.warning("Supermemory client has no 'memories' attribute; skipping chat memory logging.")
        return

    payload = {
        "question": question,
        "answer": answer,
        "references": references or [],
        "follow_up": follow_up,
    }
    document = {
        "type": "chat",
        "text": json.dumps(payload, ensure_ascii=False),
        "metadata": {
            "channel": "email-assistant",
            "has_follow_up": bool(follow_up),
        },
    }

    strategies: List[Callable[[], Any]] = []
    if hasattr(memories_api, "add"):
        strategies.append(lambda: memories_api.add(user_id=user_id, memories=[document]))
    if hasattr(memories_api, "create"):
        strategies.append(lambda: memories_api.create(user_id=user_id, memories=[document]))
    if hasattr(memories_api, "upsert"):
        strategies.append(lambda: memories_api.upsert(user_id=user_id, memories=[document]))

    for call in strategies:
        try:
            call()
            return
        except TypeError as exc:
            logger.debug("Supermemory chat memory type error, trying next strategy: %s", exc)
        except Exception as exc:
            logger.debug("Supermemory chat memory attempt failed: %s", exc)

    logger.warning("Supermemory chat memory write failed; no compatible API signature found.")
