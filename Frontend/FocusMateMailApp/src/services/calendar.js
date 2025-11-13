import { CALENDAR_ENDPOINT } from "../config/api";

const sampleEvents = [
  {
    id: "event-1",
    title: "Morning Focus Block",
    description: "Deep work session for sprint planning deck.",
    start: "2025-11-08T08:00:00-07:00",
    end: "2025-11-08T09:30:00-07:00",
    location: "Home Office",
    category: "Focus",
  },
  {
    id: "event-2",
    title: "Sprint Review Prep",
    description: "Outline key talking points for Monday's demo.",
    start: "2025-11-08T10:00:00-07:00",
    end: "2025-11-08T10:45:00-07:00",
    location: "Shared Workspace",
    category: "Planning",
  },
  {
    id: "event-3",
    title: "Walk + Podcast",
    description: "30 minute recharge walk while listening to podcast queue.",
    start: "2025-11-09T12:30:00-07:00",
    end: "2025-11-09T13:15:00-07:00",
    location: "Neighborhood Loop",
    category: "Wellness",
  },
  {
    id: "event-4",
    title: "Project Sync",
    description: "Quick alignment with design partner on new flows.",
    start: "2025-11-10T09:30:00-07:00",
    end: "2025-11-10T10:00:00-07:00",
    location: "Google Meet",
    category: "Collaboration",
  },
  {
    id: "event-5",
    title: "Therapy Session",
    description: "Weekly CBT session — bring reflection journal.",
    start: "2025-11-12T17:00:00-07:00",
    end: "2025-11-12T18:00:00-07:00",
    location: "Downtown Office",
    category: "Health",
  },
];

function normalizeEvent(event) {
  if (!event) {
    return null;
  }

  const startDate = event.start || event.start_time || event.startDateTime || event.due_datetime;
  const endDate = event.end || event.end_time || event.endDateTime || event.scheduled_end;

  const startIso =
    typeof startDate === "string"
      ? startDate
      : startDate instanceof Date
      ? startDate.toISOString()
      : null;

  const endIso =
    typeof endDate === "string"
      ? endDate
      : endDate instanceof Date
      ? endDate.toISOString()
      : null;

  if (!startIso) {
    return null;
  }

  return {
    id: String(event.id || event.event_id || event.calendar_event_id || event.title),
    title: event.title || event.summary || event.action || "Untitled Event",
    description: event.description || event.notes || "",
    start: startIso,
    end: endIso,
    location: event.location || "",
    category: event.category || event.type || event.priority || "General",
  };
}

export async function fetchCalendarEvents({ signal } = {}) {
  try {
    const response = await fetch(CALENDAR_ENDPOINT, { signal });
    if (!response.ok) {
      throw new Error(`Calendar request failed with status ${response.status}`);
    }
    const payload = await response.json();
    const events = Array.isArray(payload?.events) ? payload.events : Array.isArray(payload) ? payload : [];
    const normalized = events
      .map((item) => normalizeEvent(item))
      .filter((item) => item?.start);
    return normalized.length > 0 ? normalized : sampleEvents;
  } catch (error) {
    console.warn("Falling back to sample calendar data:", error?.message || error);
    return sampleEvents;
  }
}

