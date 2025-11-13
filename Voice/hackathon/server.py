# server.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from voice import VoiceTranscriber

app = FastAPI(title="Voice STT Server", version="1.0.0")

# CORS (adjust origins to your React dev/prod URLs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init the transcriber once
try:
    transcriber = VoiceTranscriber()
except Exception as e:
    raise RuntimeError(f"STT init failed: {e}")

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    """
    POST /stt with form-data: file=<audio blob>
    Accepts browser-recorded audio (webm/wav/mp3/m4a). Returns {"text": "..."}.
    """
    try:
        data = await file.read()
        text = transcriber.transcribe_bytes(data)
        return JSONResponse({"text": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt/mic")
async def stt_mic(seconds: float = Form(5.0)):
    """
    (Optional) Server-side mic recording for quick tests.
    Records from the machine running this server for 'seconds' seconds.
    """
    try:
        text = transcriber.record_and_transcribe(seconds=seconds)
        return JSONResponse({"text": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
