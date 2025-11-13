"""Streamlit dashboard for FocusMate mail assistant."""

from __future__ import annotations

import itertools
import time
from typing import Dict, List, Tuple

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from config import DEFAULT_UNREAD_WINDOW_DAYS
from db import initialize_database
from services.email_processor import EmailProcessor, ProcessedEmail
from services.email_search import run_email_search
from tools import GmailClient, build_query, list_message_ids

load_dotenv()
initialize_database()

processor = EmailProcessor()
gmail_client: GmailClient = processor.gmail


def gather_emails(
    limit_per_category: int = 3,
    *,
    days: int = DEFAULT_UNREAD_WINDOW_DAYS,
    include_read: bool = False,
    max_total: int = 10,
) -> Tuple[Dict[str, List[ProcessedEmail]], int]:
    categorized: Dict[str, List[ProcessedEmail]] = {"task": [], "article": [], "instruction": []}
    query = build_query(include_read=include_read, days=days)
    max_messages = min(limit_per_category * 6, max_total)

    processed_count = 0
    for message_id in list_message_ids(gmail_client, query, limit=max_messages):
        if processed_count >= max_messages:
            break
        processed = processor.process_message(message_id, mark_as_read=False)
        processed_count += 1
        if processed is None:
            continue
        category = processed.classification
        if category not in categorized:
            continue
        if len(categorized[category]) >= limit_per_category:
            continue
        categorized[category].append(processed)
        if all(len(items) >= limit_per_category for items in categorized.values()):
            break
    return categorized, processed_count


def render_task(email: ProcessedEmail) -> None:
    st.write(f"**Priority:** {email.priority_bucket} · Score {email.priority_score}")
    summary = next((note for note in email.notes if note.lower().startswith("adhd-friendly summary")), None)
    ack = next((note for note in email.notes if "acknowledgement" in note.lower()), None)
    if summary:
        st.write(summary.replace("ADHD-friendly summary: ", ""))
    if ack:
        st.info(ack)


def render_article(email: ProcessedEmail) -> None:
    summary = next((note for note in email.notes if note.lower().startswith("adhd-friendly summary")), None)
    theme = email.theme_image
    if summary:
        st.write(summary.replace("ADHD-friendly summary: ", ""))
    if theme:
        st.image(theme, caption="Theme visual", use_container_width=True)


def render_instruction(email: ProcessedEmail) -> None:
    if not email.flowchart:
        st.write("No flowchart available.")
        return
    try:
        data = json.loads(email.flowchart)
    except json.JSONDecodeError:
        st.code(email.flowchart)
        return
    steps = data.get("steps") or []
    if not steps:
        st.write("No structured steps available.")
        return
    for idx, step in enumerate(steps, start=1):
        st.markdown(
            f"""
            <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:16px;">
                <div style="
                    width:26px;height:26px;border-radius:50%;
                    background:linear-gradient(135deg,#5b8cff,#8d63ff);
                    color:#fff;font-weight:600;display:flex;
                    align-items:center;justify-content:center;">
                    {idx}
                </div>
                <div style="background:rgba(255,255,255,0.06);padding:14px 16px;border-radius:12px;flex:1;">
                    <strong>Step {idx}</strong>
                    <p style="margin:6px 0 0 0;">{step}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


CATEGORY_RENDERERS = {
    "task": render_task,
    "article": render_article,
    "instruction": render_instruction,
}

st.set_page_config(page_title="FocusMate Inbox", layout="wide")
st.title("FocusMate Mail Assistant")

limit = st.sidebar.slider("Emails per category", min_value=1, max_value=5, value=3, step=1)
include_read = st.sidebar.checkbox("Include read emails", value=False)
days = st.sidebar.slider("Lookback window (days)", min_value=1, max_value=30, value=DEFAULT_UNREAD_WINDOW_DAYS)

if "cached_emails" not in st.session_state:
    with st.spinner("Fetching emails..."):
        emails, requested = gather_emails(
            limit_per_category=limit, days=days, include_read=include_read, max_total=10
        )
        st.session_state.cached_emails = emails
        st.session_state.last_refresh = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.last_requested_count = requested
if "last_requested_count" not in st.session_state:
    st.session_state.last_requested_count = 0

if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "search_error" not in st.session_state:
    st.session_state.search_error = None

if st.sidebar.button("Refresh"):
    with st.spinner("Refreshing emails..."):
        emails, requested = gather_emails(
            limit_per_category=limit, days=days, include_read=include_read, max_total=10
        )
        st.session_state.cached_emails = emails
        st.session_state.last_refresh = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.last_requested_count = requested

st.sidebar.markdown(f"**Last refresh:** {st.session_state.last_refresh}")
requested = st.session_state.get("last_requested_count", 0)
st.sidebar.markdown(f"**Messages fetched:** {requested}")

col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]
for (category, emails), column in zip(st.session_state.cached_emails.items(), columns):
    label = category.capitalize()
    with column:
        st.header(f"{label} ({len(emails)})")
        if not emails:
            st.write("No emails found.")
            continue
        for email in emails:
            with st.expander(email.subject):
                renderer = CATEGORY_RENDERERS.get(category)
                if renderer:
                    renderer(email)
                else:
                    st.write("No renderer for this category.")
                st.write(f"*Priority reasoning:* {email.priority_reasoning}")

st.divider()
st.subheader("Ask your inbox")
query = st.text_input("Pose a question about your emails (e.g. 'What deadlines are coming up this week?')")

if st.button("Ask FocusMate"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                result = run_email_search(query.strip())
                st.session_state.search_result = result.model_dump()
                st.session_state.search_error = None
            except Exception as exc:  # pragma: no cover - best-effort handling
                st.session_state.search_result = None
                st.session_state.search_error = str(exc)

if st.session_state.search_error:
    st.error(st.session_state.search_error)
elif st.session_state.search_result:
    result = st.session_state.search_result
    st.write(result.get("answer", "No answer provided."))
    if result.get("follow_up_question"):
        st.info(f"Follow-up: {result['follow_up_question']}")
    refs = result.get("referenced_messages") or []
    if refs:
        st.caption("References:")
        for msg in refs:
            st.write(f"• {msg}")

