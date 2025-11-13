# intent_emotion.py
import os, json, re, datetime
from dateutil import parser as dtparse
from dotenv import load_dotenv
import os
import json
import datetime
import uuid

load_dotenv()

try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError(
        "Missing OpenAI SDK. Run: pip install openai"
    ) from e


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SCHEMA = {
    "name": "EmotionTaskSchema",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "language": {"type": "string"},
            "emotion": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "primary": {
                        "type": "string",
                        "enum": ["joy","sadness","anger","fear","disgust","surprise","neutral","mixed"]
                    },
                    "scores": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "joy": {"type": "number"},
                            "sadness": {"type": "number"},
                            "anger": {"type": "number"},
                            "fear": {"type": "number"},
                            "disgust": {"type": "number"},
                            "surprise": {"type": "number"},
                            "neutral": {"type": "number"}
                        },
                        "required": ["joy","sadness","anger","fear","disgust","surprise","neutral"]
                    },
                    "valence": {"type": "string", "enum": ["negative","neutral","positive","mixed"]},
                    "arousal": {"type": "string", "enum": ["low","medium","high","unknown"]}
                },
                "required": ["primary","scores","valence","arousal"]
            },
            "context": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "topic": {"type": "string"},
                    "people": {"type": "array", "items": {"type": "string"}},
                    "entities": {"type": "array", "items": {"type": "string"}},
                    "urgency_hint": {"type": "string"},
                    "blockers": {"type": "array", "items": {"type": "string"}},
                    "tone": {"type": "string"}
                },
                "required": ["topic","people","entities","urgency_hint","blockers","tone"]
            },
            "task": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "is_task": {"type": "boolean"},
                    "action": {"type": "string"},
                    "due": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low","medium","high","unspecified"]},
                    "confidence": {"type": "number"},
                    "rationale": {"type": "string"}
                },
                "required": ["is_task","action","due","priority","confidence","rationale"]
            },
            "safety": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "needs_moderation": {"type": "boolean"},
                    "notes": {"type": "string"}
                },
                "required": ["needs_moderation","notes"]
            }
        },
        "required": ["language","emotion","context","task","safety"]
    }
}


SYSTEM_PROMPT = """\
You analyze short utterances and return STRICT JSON matching the schema.

Goals:
1) Emotion: label primary emotion; include per-emotion scores (0-1), valence, arousal.
2) Context: infer topic, people/entities, urgency hints, tone, and blockers if implied.
3) Task detection: Decide if the user is expressing an actionable to-do THEY must perform.
   - If yes, produce a concise imperative 'action' (e.g., "email Alex the report"),
     a due date if stated or clearly implied, else "".
   - Infer priority: high=urgent/critical, medium=normal, low=nice-to-have.
   - Provide confidence 0-1 and a one-sentence rationale.
4) Safety: if the text suggests self-harm/violence/abuse, set needs_moderation=true.

Rules:
- Keep 'action' empty string when is_task=false.
- Put ISO 8601 date-time in 'due' when a concrete date/time is explicitly present; else "".
- NEVER invent deadlines not stated; 'urgency_hint' may reflect fuzzy terms like "today" or "ASAP".
- Be terse but informative.
"""

FALLBACK_TASK_PATTERNS = re.compile(
    r"\b(i need to|i have to|i must|remind me to|don't let me forget|i should|let me|todo:|to-do:|send|call|email|buy|pay|schedule|book|submit|finish|complete|follow up|follow-up)\b",
    re.IGNORECASE
)


# Calming guidelines based on emotion
CALMING_GUIDELINES = {
    "sadness": {
        "immediate": [
            "Take slow, deep breaths - inhale for 4 counts, hold for 4, exhale for 6",
            "Acknowledge your feelings without judgment - it's okay to feel sad",
            "Reach out to someone you trust or write down your thoughts"
        ],
        "strategies": [
            "Practice self-compassion - speak to yourself as you would to a friend",
            "Engage in gentle physical activity like a short walk",
            "Listen to calming or uplifting music",
            "Do something small that brings you comfort (warm drink, cozy blanket)"
        ],
        "professional_help": "If sadness persists for more than 2 weeks or interferes with daily life, consider talking to a mental health professional."
    },
    "anger": {
        "immediate": [
            "Step away from the situation if possible",
            "Take 5 deep breaths - count slowly with each breath",
            "Clench and release your fists to release physical tension"
        ],
        "strategies": [
            "Use 'I' statements to express feelings without blaming",
            "Channel energy into physical activity (walk, exercise, clean)",
            "Write down what's bothering you, then tear up the paper",
            "Count to 10 (or 100) before responding to the situation"
        ],
        "professional_help": "If anger feels uncontrollable or leads to aggression, anger management therapy can help."
    },
    "fear": {
        "immediate": [
            "Ground yourself: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste",
            "Place both feet flat on the floor and feel the ground beneath you",
            "Use the 4-7-8 breathing: inhale 4 counts, hold 7, exhale 8"
        ],
        "strategies": [
            "Challenge anxious thoughts - ask 'What's the evidence for this fear?'",
            "Focus on what you can control right now",
            "Talk to someone about your concerns",
            "Break overwhelming situations into smaller, manageable steps"
        ],
        "professional_help": "If fear/anxiety is persistent or limiting your life, cognitive behavioral therapy (CBT) is highly effective."
    },
    "mixed": {
        "immediate": [
            "Pause and acknowledge that you're experiencing multiple emotions",
            "Take 3 slow, deep breaths to create space between emotions",
            "Find a quiet space if possible to process your feelings"
        ],
        "strategies": [
            "Journal to untangle complex emotions",
            "Talk through your feelings with someone you trust",
            "Practice mindfulness - observe emotions without trying to change them",
            "Give yourself permission to feel multiple things at once"
        ],
        "professional_help": "A therapist can help you navigate complex emotional experiences."
    },
    "disgust": {
        "immediate": [
            "Remove yourself from the triggering situation if safe to do so",
            "Take deep breaths through your mouth if the disgust is physical",
            "Splash cool water on your face or wrists"
        ],
        "strategies": [
            "Examine if the disgust is protecting you from something harmful",
            "Distract yourself with a pleasant sensory experience",
            "Practice acceptance that some discomfort is normal",
            "Talk about what triggered the feeling"
        ],
        "professional_help": "Persistent disgust reactions may benefit from exposure therapy with a professional."
    },
    "neutral": {
        "immediate": [
            "This is a good baseline - maintain it with regular self-care",
            "Check in with yourself: are you suppressing any emotions?"
        ],
        "strategies": [
            "Practice gratitude - notice three good things today",
            "Maintain healthy routines (sleep, nutrition, movement)",
            "Stay connected with supportive people"
        ],
        "professional_help": "Regular check-ins with a therapist can help maintain emotional wellness."
    }
}


class EmotionTaskDetector:
    def __init__(self, model: str = DEFAULT_MODEL, moderation: bool = True, tasks_dir: str = "tasks"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY in your environment.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.use_moderation = moderation
        self.tasks_dir = tasks_dir
        
        # Create tasks directory if it doesn't exist
        os.makedirs(self.tasks_dir, exist_ok=True)
        abs_tasks_dir = os.path.abspath(self.tasks_dir)
        print(f"[DEBUG] EmotionTaskDetector initialized with tasks_dir: {abs_tasks_dir}")

    def _moderate(self, text: str) -> dict:
        try:
            mod = self.client.moderations.create(model="omni-moderation-latest", input=text)
            flagged = bool(mod.results[0].flagged if mod.results else False)
            return {"needs_moderation": flagged, "notes": "Flagged by moderation API" if flagged else "OK"}
        except Exception as e:
            return {"needs_moderation": False, "notes": f"Moderation unavailable: {e.__class__.__name__}"}

    def _extract_iso_due(self, text: str) -> str:
        try:
            m = re.search(
                r"\b(\d{1,2}[/\-]\d{1,2}([/\-]\d{2,4})?|\b(?:today|tomorrow|tonight|next\s+(?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b)",
                text, re.IGNORECASE
            )
            if not m:
                return ""
            phrase = m.group(0)
            base = datetime.datetime.now()
            if phrase.lower() == "today":
                dt = base
            elif phrase.lower() == "tomorrow":
                dt = base + datetime.timedelta(days=1)
            else:
                dt = dtparse.parse(phrase, default=base)
            return dt.isoformat()
        except Exception:
            return ""




    def extract_multiple_tasks(self, text: str) -> list:
        """
        Extract multiple tasks from a single transcript using GPT.
        Returns a list of task dictionaries.
        """
        print("="*80)
        print("[DEBUG] extract_multiple_tasks() CALLED - NEW VERSION")
        print(f"[DEBUG] Input text: {text}")
        print("="*80)
        try:
            # Use system local time
            current_time = datetime.datetime.now()
            
            # Simple prompt - only ask GPT for action and priority, NOT dates/times
            multi_task_prompt = f"""Extract all tasks from this transcript.

Transcript: "{text}"

Return a JSON array where each task has:
- action (string): The task in imperative form (e.g., "Buy groceries", "Call dentist")
- priority (string): high, medium, or low

Do NOT include any date or time information. Only extract the action and priority.

Example: [{{"action": "Buy groceries", "priority": "medium"}}]

Return ONLY the JSON array, nothing else."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract task actions and priorities from text. Return only JSON arrays."},
                    {"role": "user", "content": multi_task_prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            content = re.sub(r"^```json\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            
            tasks = json.loads(content)
            
            # Parse date/time from the original transcript text
            def parse_date_from_text(text_lower, current):
                """Extract date from transcript using dateutil and regex"""
                base_date = current.date()
                
                # Check for relative days first (highest priority)
                if "today" in text_lower:
                    return base_date
                if "tomorrow" in text_lower:
                    return base_date + datetime.timedelta(days=1)
                
                # Check for day of week with priority order
                weekdays = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                
                # Look for day names in the text
                for day_name, day_idx in weekdays.items():
                    # Check if this day name appears in the text
                    if day_name in text_lower:
                        current_idx = current.weekday()
                        days_ahead = (day_idx - current_idx) % 7
                        
                        # Handle "next [day]" - always next week
                        if "next " + day_name in text_lower or "next" + day_name in text_lower:
                            if days_ahead == 0:
                                days_ahead = 7  # Next week same day
                            else:
                                days_ahead += 7  # Next week that day
                        # Handle "this [day]" or just "[day]" - this week
                        elif "this " + day_name in text_lower or "this" + day_name in text_lower:
                            # This coming [day] - if it's today (0), move to next week
                            if days_ahead == 0:
                                days_ahead = 7
                        else:
                            # Just the day name - upcoming occurrence
                            if days_ahead == 0:
                                # Today is that day, assume next week
                                days_ahead = 7
                            # Otherwise days_ahead is already correct for upcoming day
                        
                        result_date = base_date + datetime.timedelta(days=days_ahead)
                        print(f"[DEBUG] Parsed '{day_name}' -> {result_date} (current={current.date()}, days_ahead={days_ahead})")
                        return result_date
                
                # Try to parse explicit dates - ensure we use current year
                try:
                    # Parse with current datetime as default to get correct year
                    parsed = dtparse.parse(text_lower, fuzzy=True, default=current)
                    
                    # If parsed date is in the past by more than a week, assume next year
                    if parsed.date() < base_date - datetime.timedelta(days=7):
                        # Date is way in the past, likely wrong year - add one year
                        parsed = parsed.replace(year=current.year + 1)
                    
                    # Always ensure date is not in the past (unless it's recent past)
                    if parsed.date() >= base_date - datetime.timedelta(days=1):
                        return parsed.date()
                except Exception as e:
                    print(f"[DEBUG] Date parsing error: {e}")
                    pass
                
                return None
            
            def parse_time_from_text(text_lower, current):
                """Extract time from transcript"""
                # Look for time patterns
                time_patterns = [
                    r"(\d{1,2})\s*pm",
                    r"(\d{1,2})\s*am",
                    r"(\d{1,2}):(\d{2})\s*pm",
                    r"(\d{1,2}):(\d{2})\s*am",
                    r"at\s+(\d{1,2})\s*pm",
                    r"at\s+(\d{1,2})\s*am",
                    r"(\d{1,2}):(\d{2})",
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        groups = match.groups()
                        hour = int(groups[0])
                        minute = int(groups[1]) if len(groups) > 1 and groups[1] else 0
                        
                        # Handle PM/AM
                        if "pm" in pattern and hour != 12:
                            hour += 12
                        elif "am" in pattern and hour == 12:
                            hour = 0
                        
                        return datetime.time(hour % 24, minute)
                
                return None
            
            # Parse date and time from the original transcript
            text_lower = text.lower()
            print(f"[DEBUG] Transcript (lowercase): {text_lower}")
            print(f"[DEBUG] Current time: {current_time} (weekday={current_time.weekday()})")
            parsed_date = parse_date_from_text(text_lower, current_time)
            parsed_time = parse_time_from_text(text_lower, current_time)
            print(f"[DEBUG] Parsed date: {parsed_date}, Parsed time: {parsed_time}")
            
            # Build due_info structure with separate date and time
            formatted_tasks = []
            for task in tasks:
                if isinstance(task, dict) and task.get("action"):
                    # Determine final date and time
                    if parsed_date and parsed_time:
                        # Both date and time specified
                        due_info = {
                            "date": parsed_date.strftime("%Y-%m-%d"),
                            "time": parsed_time.strftime("%H:%M"),
                            "all_day": False
                        }
                    elif parsed_date and not parsed_time:
                        # Only date specified - all day event
                        due_info = {
                            "date": parsed_date.strftime("%Y-%m-%d"),
                            "time": "",
                            "all_day": True
                        }
                    elif not parsed_date and parsed_time:
                        # Only time specified - use today or tomorrow
                        if parsed_time < current_time.time():
                            # Time has passed, use tomorrow
                            target_date = current_time.date() + datetime.timedelta(days=1)
                        else:
                            # Use today
                            target_date = current_time.date()
                        
                        due_info = {
                            "date": target_date.strftime("%Y-%m-%d"),
                            "time": parsed_time.strftime("%H:%M"),
                            "all_day": False
                        }
                    else:
                        # No date or time specified
                        due_info = {
                            "date": "",
                            "time": "",
                            "all_day": False
                        }
                    
                    formatted_tasks.append({
                        "action": task["action"],
                        "due": due_info,
                        "priority": task.get("priority", "medium"),
                        "is_task": True,
                        "confidence": 0.9,
                        "rationale": "Extracted from transcript analysis"
                    })
            
            return formatted_tasks
            
        except Exception as e:
            print(f"Error extracting multiple tasks: {e}")
            return []
        
    def save_task_to_file(self, task: dict, transcript: str = "") -> str:
        """
        Save a task to a JSON file in the tasks directory.
        Returns the filename of the saved task.
        """
        timestamp = datetime.datetime.now()
        # Use UUID to ensure uniqueness
        task_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        filename = f"task_{task_id}.json"
        filepath = os.path.join(self.tasks_dir, filename)
        
        # Get due info (handle both old and new format)
        due_info = task.get("due", {})
        if isinstance(due_info, str):
            # Old format - convert to new structure
            if due_info:
                # Try to parse as ISO datetime or other datetime formats
                try:
                    # Try ISO format first (with T separator)
                    if "T" in due_info:
                        task_datetime = datetime.datetime.fromisoformat(due_info.replace("Z", "+00:00"))
                    # Try space-separated format
                    elif " " in due_info:
                        task_datetime = datetime.datetime.strptime(due_info, "%Y-%m-%d %H:%M")
                    else:
                        # Just a date string
                        task_datetime = datetime.datetime.strptime(due_info, "%Y-%m-%d")
                    
                    # Check if time component exists (not midnight)
                    has_time = task_datetime.hour != 0 or task_datetime.minute != 0
                    
                    due_info = {
                        "date": task_datetime.strftime("%Y-%m-%d"),
                        "time": task_datetime.strftime("%H:%M") if has_time else "",
                        "all_day": not has_time
                    }
                except (ValueError, AttributeError) as e:
                    print(f"[WARNING] Failed to parse due date '{due_info}': {e}")
                    # Fallback - treat as date only
                    due_info = {
                        "date": due_info,
                        "time": "",
                        "all_day": True
                    }
            else:
                # Empty string
                due_info = {
                    "date": "",
                    "time": "",
                    "all_day": False
                }
        
        # Prepare task data with metadata
        task_data = {
            "id": task_id,
            "created_at": timestamp.isoformat(),
            "action": task.get("action", ""),
            "due": due_info,  # New structured format
            "priority": task.get("priority", "medium"),
            "confidence": task.get("confidence", 0.0),
            "rationale": task.get("rationale", ""),
            "transcript": transcript,
            "completed": False
        }
        
        # Save to file
        try:
            print(f"[DEBUG] Attempting to save task to: {filepath}")
            print(f"[DEBUG] Task data: {task_data}")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Task saved: {filename}")
            return filename
        except Exception as e:
            print(f"[ERROR] Error saving task: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def get_calming_guidelines(self, emotion: str, arousal: str = "medium") -> dict:
        """
        Returns personalized calming guidelines based on detected emotion.
        """
        emotion_key = emotion.lower()
        if emotion_key not in CALMING_GUIDELINES:
            emotion_key = "neutral"
        
        guidelines = CALMING_GUIDELINES[emotion_key].copy()
        
        # Add urgency level based on arousal
        if arousal == "high":
            guidelines["urgency"] = "high"
            guidelines["message"] = f"You're experiencing intense {emotion}. Let's work on calming down right now."
        elif arousal == "medium":
            guidelines["urgency"] = "medium"
            guidelines["message"] = f"You're feeling {emotion}. Here are some techniques that can help."
        else:
            guidelines["urgency"] = "low"
            guidelines["message"] = f"You're experiencing {emotion}. Here are some gentle strategies."
        
        return guidelines

    def analyze(self, text: str, include_guidelines: bool = True, extract_all_tasks: bool = True) -> dict:
        """
        Main entrypoint: returns a dict with keys: language, emotion, context, task, safety, 
        optionally calming_guidelines, and optionally tasks (list of all extracted tasks)
        """
        safety = self._moderate(text) if self.use_moderation else {"needs_moderation": False, "notes": "Skipped"}
        heuristic_due = self._extract_iso_due(text)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                    {"role": "system", "content": f"HeuristicDueHint: {heuristic_due or 'none'}"}
                ],
                response_format={"type": "json_schema", "json_schema": SCHEMA}
            )

            # Parse the response
            content = resp.choices[0].message.content
            parsed = json.loads(content) if isinstance(content, str) else content

            if not isinstance(parsed, dict):
                raise ValueError("Structured output missing or unparsable.")

            # Merge safety
            parsed["safety"] = parsed.get("safety") or safety
            
            # Extract multiple tasks if requested
            if extract_all_tasks:
                tasks = self.extract_multiple_tasks(text)
                print(f"[DEBUG] Extracted {len(tasks)} tasks")
                if tasks:
                    parsed["tasks"] = tasks
                    # Save each task to a file
                    for i, task in enumerate(tasks):
                        print(f"[DEBUG] Saving task {i+1}/{len(tasks)}")
                        self.save_task_to_file(task, text)
                else:
                    # Fallback to main task if extraction failed
                    main_task = parsed.get("task", {})
                    if main_task.get("is_task") and main_task.get("action"):
                        parsed["tasks"] = [main_task]
                        self.save_task_to_file(main_task, text)
                    else:
                        parsed["tasks"] = []
            
            # Add calming guidelines if requested
            if include_guidelines:
                emotion = parsed["emotion"]["primary"]
                arousal = parsed["emotion"]["arousal"]
                parsed["calming_guidelines"] = self.get_calming_guidelines(emotion, arousal)
            
            return parsed

        except Exception as e:
            # Robust fallback
            print(f"[WARNING] API Error: {e}")
            is_task = bool(FALLBACK_TASK_PATTERNS.search(text))
            action = ""
            if is_task:
                action = re.sub(r"^(i\s+(need|have|must)\s+to|remind me to|don't let me forget|todo:|to-do:)\s*", "", text, flags=re.IGNORECASE).strip()
                action = action[:140]

            # Try to detect emotion from keywords
            text_lower = text.lower()
            detected_emotion = "neutral"
            if any(word in text_lower for word in ["sad", "depressed", "down", "blue", "unhappy", "miserable"]):
                detected_emotion = "sadness"
            elif any(word in text_lower for word in ["angry", "mad", "furious", "irritated", "frustrated"]):
                detected_emotion = "anger"
            elif any(word in text_lower for word in ["scared", "afraid", "anxious", "worried", "terrified", "fear"]):
                detected_emotion = "fear"
            elif any(word in text_lower for word in ["happy", "joy", "excited", "great", "wonderful", "amazing"]):
                detected_emotion = "joy"

            fallback_task = {
                "is_task": is_task,
                "action": action if is_task else "",
                "due": self._extract_iso_due(text) if is_task else "",
                "priority": "unspecified",
                "confidence": 0.3 if is_task else 0.2,
                "rationale": "Fallback heuristic firing due to API error."
            }

            result = {
                "language": "eng",
                "emotion": {
                    "primary": detected_emotion,
                    "scores": {k: 0.0 for k in ["joy","sadness","anger","fear","disgust","surprise","neutral"]} | {detected_emotion: 0.7},
                    "valence": "negative" if detected_emotion in ["sadness", "anger", "fear"] else "neutral",
                    "arousal": "medium"
                },
                "context": {
                    "topic": "",
                    "people": [],
                    "entities": [],
                    "urgency_hint": "",
                    "blockers": [],
                    "tone": "emotional" if detected_emotion != "neutral" else "neutral"
                },
                "task": fallback_task,
                "safety": safety
            }
            
            # Add tasks list
            if extract_all_tasks and is_task and action:
                result["tasks"] = [fallback_task]
                self.save_task_to_file(fallback_task, text)
            else:
                result["tasks"] = []
            
            if include_guidelines:
                result["calming_guidelines"] = self.get_calming_guidelines(detected_emotion, "medium")
            
            return result