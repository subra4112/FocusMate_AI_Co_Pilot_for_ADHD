import { VOICE_TRANSCRIBE_ENDPOINT } from "../config/api";

export async function transcribeAudioAsync({
  uri,
  mimeType = "audio/m4a",
  fileName = "recording.m4a",
} = {}) {
  if (!uri) {
    throw new Error("No audio file provided.");
  }

  const formData = new FormData();
  formData.append("file", {
    uri,
    name: fileName,
    type: mimeType,
  });

  const response = await fetch(VOICE_TRANSCRIBE_ENDPOINT, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Voice transcription failed (${response.status}).`);
  }

  return response.json();
}
