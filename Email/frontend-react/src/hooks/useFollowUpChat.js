import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function sanitizeHistory(messages) {
  return messages
    .filter((entry) => entry.role === "user" || entry.role === "assistant")
    .map((entry) => ({ role: entry.role, message: entry.text }));
}

export default function useFollowUpChat() {
  const [messages, setMessages] = useState([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(null);
  const messagesRef = useRef(messages);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const ask = useCallback(async (question) => {
    const trimmed = question.trim();
    if (!trimmed || pending) {
      return;
    }

    const historyPayload = sanitizeHistory(messagesRef.current);
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setPending(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/qa`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmed,
          history: historyPayload,
        }),
      });

      if (!response.ok) {
        throw new Error(`API responded with status ${response.status}`);
      }

      const payload = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: payload.answer,
          followUp: payload.follow_up_question,
          references: payload.referenced_messages || [],
        },
      ]);
    } catch (err) {
      setError(err.message || "Unable to fetch answer");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "I ran into a problem answering that. Please try again shortly.",
        },
      ]);
    } finally {
      setPending(false);
    }
  }, [pending]);

  const reset = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const latestFollowUp = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      const entry = messages[i];
      if (entry.role === "assistant" && entry.followUp) {
        return entry.followUp;
      }
    }
    return null;
  }, [messages]);

  return {
    messages,
    loading: pending,
    error,
    ask,
    reset,
    suggestion: latestFollowUp,
  };
}
