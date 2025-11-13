export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL?.trim() || "http://127.0.0.1:8000";

export const EMAILS_ENDPOINT = `${API_BASE_URL}/emails`;
export const CALENDAR_ENDPOINT = `${API_BASE_URL}/calendar/events`;
const voiceOverride = process.env.EXPO_PUBLIC_VOICE_API_URL?.trim();
export const VOICE_API_BASE_URL = voiceOverride && voiceOverride.length > 0 ? voiceOverride : API_BASE_URL;
export const VOICE_TRANSCRIBE_ENDPOINT = `${VOICE_API_BASE_URL}/stt`;

