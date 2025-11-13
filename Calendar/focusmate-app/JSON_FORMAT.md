# 📋 Task JSON Format Documentation

## Your Current Format (KEEP THIS!)

Your tasks are already in a great format! Here's what each field means:

```json
{
  "id": "20251109_141643_947332",
  "created_at": "2025-11-09T14:16:43.947332",
  "action": "Get groceries",
  "due_date": "2025-11-09",
  "due_time": "15:00",
  "due_datetime": "2025-11-09T15:00:00",
  "estimated_minutes": 30,
  "calendar_event_id": null,
  "scheduled_start": null,
  "scheduled_end": null,
  "priority": "medium",
  "confidence": 0.9,
  "rationale": "Extracted from multi-task analysis",
  "transcript": "Uh, what do I do now?...",
  "completed": false,
  "status": "todo"
}
```

## Field Explanations

### ✅ Required Fields (You Already Have These)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier | `"20251109_141643_947332"` |
| `action` | string | What to do | `"Get groceries"` |
| `priority` | string | Importance level | `"high"`, `"medium"`, or `"low"` |
| `completed` | boolean | Is it done? | `true` or `false` |

### 📅 Date/Time Fields (Enhanced Format)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `due_date` | string | Date in ISO format | `"2025-11-09"` |
| `due_time` | string | Time in 24h format | `"15:00"` |
| `due_datetime` | string | Full datetime ISO | `"2025-11-09T15:00:00"` |
| `created_at` | string | When task was created | `"2025-11-09T14:16:43.947332"` |

### 📊 Planning Fields (For Calendar Integration)

| Field | Type | Description | When Used |
|-------|------|-------------|-----------|
| `estimated_minutes` | number | How long it takes | `30`, `60`, `90` |
| `scheduled_start` | string/null | When planner schedules it | `"2025-11-09T10:00:00"` |
| `scheduled_end` | string/null | When planner ends it | `"2025-11-09T10:30:00"` |
| `calendar_event_id` | string/null | Google Calendar ID | `"abc123xyz"` |

### 🤖 AI Fields (From Voice Processing)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `confidence` | number | AI certainty (0-1) | `0.9` |
| `rationale` | string | Why AI extracted this | `"Extracted from multi-task analysis"` |
| `transcript` | string | Original voice input | `"I need to finish my assignment"` |
| `status` | string | Current state | `"todo"`, `"in_progress"`, `"done"` |

## ✨ What Changed From Your Original Format?

Your original format had:
```json
{
  "due": ""  // Empty string - not helpful!
}
```

Now it has:
```json
{
  "due_date": "2025-11-09",           // Clean date
  "due_time": "15:00",                // Clean time
  "due_datetime": "2025-11-09T15:00:00",  // Combined (best for calendar!)
}
```

## 🎯 Why These Changes Matter

### 1. Calendar Integration
- `due_datetime` → Calendar can place it exactly
- `estimated_minutes` → Calendar knows how long to block
- `scheduled_start/end` → Tracks when "Plan My Day" scheduled it

### 2. Better Sorting
- Can sort by date: `moment(task.due_datetime).isBefore(other.due_datetime)`
- Can filter by today: `moment(task.due_datetime).isSame(moment(), 'day')`

### 3. Time Display
```javascript
// Show "Today at 3:00 PM" vs "Tomorrow at 9:00 AM"
const formatDueDate = (dueDateTime) => {
  const date = moment(dueDateTime);
  if (date.isSame(moment(), 'day')) return 'Today at ' + date.format('h:mm A');
  return date.format('MMM D, h:mm A');
};
```

## 📝 Examples of Good Task Objects

### High Priority Task (Due Soon)
```json
{
  "id": "task_001",
  "created_at": "2025-11-09T08:00:00",
  "action": "Finish CSE 578 assignment",
  "due_date": "2025-11-09",
  "due_time": "23:59",
  "due_datetime": "2025-11-09T23:59:00",
  "estimated_minutes": 120,
  "calendar_event_id": null,
  "scheduled_start": null,
  "scheduled_end": null,
  "priority": "high",
  "confidence": 0.95,
  "rationale": "Assignment deadline detected",
  "transcript": "I need to finish my data viz assignment by tonight",
  "completed": false,
  "status": "todo"
}
```

### Medium Priority Task (Has Time)
```json
{
  "id": "task_002",
  "created_at": "2025-11-09T09:00:00",
  "action": "Grocery shopping",
  "due_date": "2025-11-10",
  "due_time": "15:00",
  "due_datetime": "2025-11-10T15:00:00",
  "estimated_minutes": 45,
  "calendar_event_id": null,
  "scheduled_start": null,
  "scheduled_end": null,
  "priority": "medium",
  "confidence": 0.85,
  "rationale": "Routine task from voice",
  "transcript": "I should go grocery shopping tomorrow afternoon",
  "completed": false,
  "status": "todo"
}
```

### Scheduled Task (After Plan My Day)
```json
{
  "id": "task_003",
  "created_at": "2025-11-09T10:00:00",
  "action": "Review D3.js documentation",
  "due_date": "2025-11-09",
  "due_time": "16:00",
  "due_datetime": "2025-11-09T16:00:00",
  "estimated_minutes": 60,
  "calendar_event_id": null,
  "scheduled_start": "2025-11-09T14:00:00",  // Planner scheduled it at 2pm
  "scheduled_end": "2025-11-09T15:00:00",    // For 1 hour
  "priority": "medium",
  "confidence": 0.9,
  "rationale": "Study task",
  "transcript": "I want to review D3 docs this afternoon",
  "completed": false,
  "status": "todo"
}
```

## 🔄 How Your Backend Should Generate This

When processing voice input, your AI should extract:

```python
# Example prompt structure
prompt = f"""
Extract a task from this transcript: "{transcript}"

Return JSON with:
- action: what to do (string)
- due_date: YYYY-MM-DD format
- due_time: HH:MM in 24h format (if mentioned, else estimate)
- estimated_minutes: 30-120 (estimate based on task complexity)
- priority: high/medium/low
- confidence: 0-1 (how confident you are)
- rationale: why you extracted this

Transcript: "I need to finish my report by tomorrow at 3pm"

Output valid JSON only.
"""

# Expected output:
{
  "action": "Finish report",
  "due_date": "2025-11-10",
  "due_time": "15:00",
  "due_datetime": "2025-11-10T15:00:00",
  "estimated_minutes": 90,
  "priority": "high",
  "confidence": 0.95,
  "rationale": "Explicit deadline mentioned"
}
```

## ⚠️ Important Notes

### 1. Date Format MUST be ISO 8601
✅ Good: `"2025-11-09T15:00:00"`
❌ Bad: `"11/9/2025 3:00 PM"`

### 2. Priority Values
Only use these exact strings:
- `"high"` - Urgent, do today
- `"medium"` - Important, but not urgent  
- `"low"` - Nice to have

### 3. Null vs Empty String
✅ Good: `"calendar_event_id": null`
❌ Bad: `"calendar_event_id": ""`

### 4. Boolean Values
✅ Good: `"completed": false`
❌ Bad: `"completed": "false"` (string)

## 🚀 Using in Your App

### Add a task from frontend:
```javascript
const newTask = {
  id: Date.now().toString(),
  created_at: new Date().toISOString(),
  action: "Buy milk",
  due_date: "2025-11-09",
  due_time: "18:00",
  due_datetime: "2025-11-09T18:00:00",
  estimated_minutes: 15,
  calendar_event_id: null,
  scheduled_start: null,
  scheduled_end: null,
  priority: "low",
  confidence: 1.0,
  rationale: "Manually added",
  transcript: "",
  completed: false,
  status: "todo"
};

setTasks([...tasks, newTask]);
```

### Load from JSON file:
```javascript
import taskData from './task_20251109_141643_947332.json';
setTasks([...tasks, taskData]);
```

## 📚 Summary

Your enhanced JSON format is perfect for:
- ✅ Calendar integration (exact dates/times)
- ✅ Task scheduling (duration estimates)
- ✅ Priority sorting (high/medium/low)
- ✅ AI confidence tracking
- ✅ Voice transcript history
- ✅ Google Calendar sync (event IDs)

No changes needed to your current structure - it's already optimized! 🎉
