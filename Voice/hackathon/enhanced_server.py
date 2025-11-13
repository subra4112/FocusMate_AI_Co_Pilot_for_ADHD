# enhanced_server.py
# Enhanced server with additional endpoints for mobile app
import os
import json
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from voice import VoiceTranscriber
from intent_emotion import EmotionTaskDetector
from google_calendar_sync import GoogleCalendarSync

app = FastAPI(title="FocusMate Voice Server", version="2.0.0")

# CORS - Allow mobile app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    transcriber = VoiceTranscriber()
    emotion_detector = EmotionTaskDetector(tasks_dir="../tasks")
    try:
        calendar_sync = GoogleCalendarSync(tasks_dir="../tasks")
        calendar_sync.authenticate()
        calendar_available = True
        print("[OK] Google Calendar sync ready")
    except Exception as calendar_error:
        calendar_sync = None
        calendar_available = False
        print(f"[INFO] Google Calendar sync disabled: {calendar_error}")
except Exception as e:
    raise RuntimeError(f"Initialization failed: {e}")

# Models for API
class TaskResponse(BaseModel):
    id: str
    created_at: str
    action: str
    due: dict
    priority: str
    confidence: float
    rationale: str
    transcript: str
    completed: bool
    synced_to_calendar: Optional[bool] = False

class TranscriptionResponse(BaseModel):
    text: str
    emotion: Optional[dict] = None
    tasks: Optional[List[dict]] = None
    calming_guidelines: Optional[dict] = None

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    """
    POST /stt with form-data: file=<audio blob>
    Returns transcription, emotion analysis, and extracted tasks.
    """
    try:
        # Transcribe audio
        data = await file.read()
        text = transcriber.transcribe_bytes(data)
        
        if not text or text.strip() == "":
            return JSONResponse({
                "text": "",
                "message": "No speech detected"
            })
        
        # Analyze emotion and extract tasks
        analysis = emotion_detector.analyze(text, include_guidelines=True, extract_all_tasks=True)
        
        if calendar_available and calendar_sync:
            try:
                calendar_sync.sync_all_tasks(force_resync=False)
            except Exception as sync_err:
                print(f"[WARNING] Calendar sync failed: {sync_err}")

        response = {
            "text": text,
            "emotion": analysis.get("emotion"),
            "tasks": analysis.get("tasks", []),
            "calming_guidelines": analysis.get("calming_guidelines"),
            "context": analysis.get("context"),
            "safety": analysis.get("safety")
        }
        
        return JSONResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt/mic")
async def stt_mic(seconds: float = Form(5.0)):
    """
    Server-side mic recording for testing (optional).
    """
    try:
        text = transcriber.record_and_transcribe(seconds=seconds)
        
        if not text or text.strip() == "":
            return JSONResponse({
                "text": "",
                "message": "No speech detected"
            })
        
        analysis = emotion_detector.analyze(text, include_guidelines=True, extract_all_tasks=True)
        
        if calendar_available and calendar_sync:
            try:
                calendar_sync.sync_all_tasks(force_resync=False)
            except Exception as sync_err:
                print(f"[WARNING] Calendar sync failed: {sync_err}")
        
        response = {
            "text": text,
            "emotion": analysis.get("emotion"),
            "tasks": analysis.get("tasks", []),
            "calming_guidelines": analysis.get("calming_guidelines"),
            "context": analysis.get("context"),
            "safety": analysis.get("safety")
        }
        
        return JSONResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks(completed: Optional[bool] = None):
    """
    GET /tasks - Retrieve all tasks
    Optional query param: completed=true/false to filter
    """
    try:
        tasks_dir = Path("../tasks")
        tasks = []
        
        if not tasks_dir.exists():
            return JSONResponse({"tasks": []})
        
        for json_file in tasks_dir.glob("task_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    
                    # Filter by completed status if specified
                    if completed is not None:
                        if task.get("completed", False) == completed:
                            tasks.append(task)
                    else:
                        tasks.append(task)
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return JSONResponse({"tasks": tasks, "count": len(tasks)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """
    GET /tasks/{task_id} - Retrieve a specific task
    """
    try:
        tasks_dir = Path("../tasks")
        task_file = tasks_dir / f"task_{task_id}.json"
        
        if not task_file.exists():
            raise HTTPException(status_code=404, detail="Task not found")
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        
        return JSONResponse(task)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, completed: Optional[bool] = None):
    """
    PUT /tasks/{task_id} - Update task status
    """
    try:
        tasks_dir = Path("../tasks")
        
        # Find the task file (might have different timestamp format)
        task_files = list(tasks_dir.glob(f"task_*_{task_id[:8]}.json"))
        
        if not task_files:
            # Try finding by full task_id
            task_files = [f for f in tasks_dir.glob("task_*.json") 
                         if task_id in f.stem]
        
        if not task_files:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_file = task_files[0]
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        
        # Update fields
        if completed is not None:
            task["completed"] = completed
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        return JSONResponse(task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    DELETE /tasks/{task_id} - Delete a task
    """
    try:
        tasks_dir = Path("../tasks")
        task_files = list(tasks_dir.glob(f"task_*_{task_id[:8]}.json"))
        
        if not task_files:
            task_files = [f for f in tasks_dir.glob("task_*.json") 
                         if task_id in f.stem]
        
        if not task_files:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_file = task_files[0]
        os.remove(task_file)
        
        return JSONResponse({"message": "Task deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    GET /health - Health check endpoint
    """
    return JSONResponse({
        "status": "healthy",
        "service": "FocusMate Voice Server",
        "version": "2.0.0"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

