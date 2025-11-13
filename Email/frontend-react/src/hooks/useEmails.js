import { useCallback, useEffect, useState } from "react";

const DEFAULT_DATA = { task: [], article: [], instruction: [] };
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function useEmails() {
  const [data, setData] = useState(DEFAULT_DATA);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEmails = useCallback(async (options = {}) => {
    const { refresh = false } = options;
    setLoading(true);
    setError(null);
    try {
      if (refresh) {
        const refreshResponse = await fetch(`${API_BASE}/emails/refresh`, {
          method: "POST",
        });
        if (!refreshResponse.ok) {
          throw new Error("Failed to refresh emails");
        }
      }
      const response = await fetch(`${API_BASE}/emails`);
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
      const payload = await response.json();
      setData({
        task: payload.task || [],
        article: payload.article || [],
        instruction: payload.instruction || [],
      });
    } catch (err) {
      setError(err.message || "Failed to fetch emails");
      setData(DEFAULT_DATA);
    } finally {
      setLoading(false);
    }
  }, [API_BASE]);

  useEffect(() => {
    fetchEmails();
  }, [fetchEmails]);

  return {
    data,
    loading,
    error,
    refetch: () => fetchEmails({ refresh: true }),
  };
}
