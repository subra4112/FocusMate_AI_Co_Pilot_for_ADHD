import { EMAILS_ENDPOINT } from "../config/api";

function normalizeEmail(raw, fallbackClassification) {
  const classification = raw.classification || fallbackClassification || "article";
  let steps = [];

  if (raw.flowchart_type === "json" && raw.flowchart) {
    try {
      const parsed = JSON.parse(raw.flowchart);
      if (Array.isArray(parsed.steps)) {
        steps = parsed.steps.filter(Boolean);
      }
    } catch (err) {
      // Ignore malformed flowchart payloads.
    }
  }

  return {
    id: raw.message_id,
    subject: raw.subject,
    sender: raw.sender,
    receivedAt: raw.received_at,
    classification,
    summary: raw.summary,
    priorityBucket: raw.priority_bucket,
    priorityReasoning: raw.priority_reasoning,
    notes: raw.notes || [],
    steps,
    themeImage: raw.theme_image,
    calendarEventLink: raw.calendar_event_link,
    raw,
  };
}

export async function fetchEmails({ category, limit = 6, refresh = true } = {}) {
  const params = new URLSearchParams();
  if (category && category !== "all") {
    params.append("category", category);
  }
  if (limit) {
    params.append("limit", String(limit));
  }
  // Always refresh from Gmail to get latest emails
  if (refresh) {
    params.append("refresh", "true");
  }

  const url = params.toString() ? `${EMAILS_ENDPOINT}?${params}` : EMAILS_ENDPOINT;

  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  const payload = await response.json();

  const categorized = {
    task: [],
    instruction: [],
    article: [],
  };

  Object.entries(payload).forEach(([key, items]) => {
    const bucket = key.toLowerCase();
    if (!Array.isArray(items)) {
      return;
    }
    const normalized = items.map((item) => normalizeEmail(item, bucket));
    if (bucket in categorized) {
      categorized[bucket] = normalized;
    } else if (categorized.task.length === 0) {
      categorized.task = normalized;
    }
  });

  return categorized;
}

