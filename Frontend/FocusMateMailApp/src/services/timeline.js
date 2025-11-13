import { API_BASE_URL } from "../config/api";

const TIMELINE_ENDPOINT = `${API_BASE_URL}/timeline`;

export const fetchTimeline = async () => {
  try {
    const response = await fetch(TIMELINE_ENDPOINT);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching timeline:", error);
    throw error;
  }
};

export const markTaskComplete = async (taskId) => {
  try {
    const response = await fetch(`${TIMELINE_ENDPOINT}/${taskId}/complete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error marking task complete:", error);
    throw error;
  }
};


