# 📱 Google Calendar Integration - Real Examples

## Example 1: Your Sample Task

### Your JSON Input:
```json
{
  "id": "20251109_141643_947831",
  "created_at": "2025-11-09T14:16:43.947831",
  "action": "Prepare for job interview",
  "due": "09:00",
  "priority": "high",
  "confidence": 0.9,
  "rationale": "Extracted from multi-task analysis",
  "transcript": "Uh, what do I do now? Do I have to do this? Today, I have a task at 8:00 where I have to finish an assignment. Then, I have to go to get some groceries. Then, I have a really good job, uh, interview tomorrow ... at 9:00.",
  "completed": false
}
```

### Creates This Google Calendar Event:

**Title:** Prepare for job interview

**Time:** November 10, 2025, 9:00 AM - 10:00 AM (1 hour)

**Color:** 🔴 Red (high priority)

**Description:**
```
🎙️ From Voice: "Uh, what do I do now? Do I have to do this? Today, I have a task at 8:00 where I have to finish an assignment. Then, I have to go to get some groceries. Then, I have a really good job, uh, interview tomorrow ... at 9:00."

📋 Priority: high
🤖 Confidence: 90%
💡 Rationale: Extracted from multi-task analysis

📱 Created via FocusMate
```

**Reminders:**
- 🔔 30 minutes before (8:30 AM)
- 🔔 10 minutes before (8:50 AM)

---

## Example 2: Medium Priority Task

### Input:
```json
{
  "id": "task_002",
  "created_at": "2025-11-09T10:00:00",
  "action": "Get groceries",
  "due": "15:00",
  "priority": "medium",
  "confidence": 0.9,
  "rationale": "Routine task",
  "transcript": "Then, I have to go to get some groceries.",
  "completed": false
}
```

### Creates:
**Title:** Get groceries  
**Time:** November 9, 2025, 3:00 PM - 3:45 PM (45 mins)  
**Color:** 🟡 Yellow (medium priority)  

---

## Example 3: Low Priority Task

### Input:
```json
{
  "id": "task_003",
  "created_at": "2025-11-09T08:00:00",
  "action": "Review D3.js documentation",
  "due": "16:00",
  "priority": "low",
  "confidence": 0.85,
  "rationale": "Learning task",
  "transcript": "I should review the D3 docs later",
  "completed": false
}
```

### Creates:
**Title:** Review D3.js documentation  
**Time:** November 9, 2025, 4:00 PM - 4:30 PM (30 mins)  
**Color:** 🟢 Green (low priority)  

---

## Example 4: Completed Task

### Input:
```json
{
  "id": "task_004",
  "action": "Finish assignment",
  "due": "20:00",
  "priority": "high",
  "completed": true,  // ← Marked complete
  "calendar_event_id": "abc123"
}
```

### Updates Calendar To:
**Title:** ✅ Finish assignment  
**Color:** ⚫ Gray (completed)  
**Status:** Kept in calendar for history  

---

## Example 5: Sync Multiple Tasks

### You have 3 tasks:
```javascript
[
  { "action": "Job interview", "due": "09:00", "priority": "high" },
  { "action": "Get groceries", "due": "15:00", "priority": "medium" },
  { "action": "Review docs", "due": "16:00", "priority": "low" }
]
```

### Click "Sync All Tasks"

### Result in Google Calendar:
```
9:00 AM - 10:00 AM    🔴 Job interview
3:00 PM - 3:45 PM     🟡 Get groceries  
4:00 PM - 4:30 PM     🟢 Review docs
```

All with reminders, descriptions, and proper colors!

---

## Code Examples

### 1. Sync on Task Creation

```javascript
// In HomePage.jsx when adding a task
import calendarService from '../services/googleCalendar';

const createTask = async (newTask) => {
  // Add to app
  setTasks([...tasks, newTask]);
  
  // Auto-sync to calendar if signed in
  if (calendarService.isSignedIn()) {
    try {
      const eventId = await calendarService.createEventFromTask(newTask);
      newTask.calendar_event_id = eventId;
      console.log('✅ Task auto-synced to calendar');
    } catch (error) {
      console.error('Failed to sync:', error);
    }
  }
};
```

### 2. Update on Task Complete

```javascript
// In TaskList.jsx
import calendarService from '../services/googleCalendar';

const handleToggleComplete = async (taskId) => {
  const task = tasks.find(t => t.id === taskId);
  
  // Toggle in app
  task.completed = !task.completed;
  setTasks([...tasks]);
  
  // Update calendar if synced
  if (task.calendar_event_id && calendarService.isSignedIn()) {
    try {
      if (task.completed) {
        await calendarService.markEventCompleted(task.calendar_event_id, task);
        console.log('✅ Calendar event marked complete');
      }
    } catch (error) {
      console.error('Failed to update calendar:', error);
    }
  }
};
```

### 3. Delete from Calendar

```javascript
// When deleting a task
const deleteTask = async (taskId) => {
  const task = tasks.find(t => t.id === taskId);
  
  // Delete from calendar first
  if (task.calendar_event_id && calendarService.isSignedIn()) {
    try {
      await calendarService.deleteEvent(task.calendar_event_id);
      console.log('✅ Deleted from calendar');
    } catch (error) {
      console.error('Failed to delete from calendar:', error);
    }
  }
  
  // Delete from app
  setTasks(tasks.filter(t => t.id !== taskId));
};
```

---

## User Flow Examples

### Flow 1: First Time Setup
```
1. User opens FocusMate app
2. Goes to Tasks tab
3. Sees "Connect Google Calendar" card
4. Clicks "Sign in with Google"
5. Google OAuth popup appears
6. User signs in and authorizes
7. Sees "✅ Connected to Google Calendar"
8. Clicks "Sync All Tasks (3)"
9. Sees "Sync Complete! 3 synced"
10. Opens calendar.google.com
11. All tasks are there! 🎉
```

### Flow 2: Adding a New Task
```
1. User on Home screen
2. Clicks "Add Sample Task"
3. Task appears in list
4. (If auto-sync enabled) Task automatically added to calendar
5. User gets notification: "✅ Task synced to calendar"
6. No manual sync needed!
```

### Flow 3: Completing a Task
```
1. User on Tasks tab
2. Clicks checkbox next to "Job interview"
3. Task marked complete with strikethrough
4. Calendar event updates: "✅ Job interview"
5. Event color changes to gray
6. Event remains in calendar for history
```

---

## API Response Examples

### Successful Event Creation
```javascript
{
  success: true,
  eventId: "abc123xyz456",
  htmlLink: "https://calendar.google.com/calendar/event?eid=abc123",
  created: "2025-11-09T14:16:43.000Z"
}
```

### Sync Results
```javascript
{
  results: [
    { taskId: "task_001", eventId: "event_001", success: true },
    { taskId: "task_002", eventId: "event_002", success: true },
    { taskId: "task_003", error: "Rate limit", success: false }
  ],
  successCount: 2,
  failCount: 1
}
```

---

## Testing Checklist

Try these scenarios:

- [ ] Sign in with Google
- [ ] Sync a single high-priority task
- [ ] Check calendar shows red event
- [ ] Check event description has transcript
- [ ] Check reminders are set (30 min, 10 min)
- [ ] Mark task complete in app
- [ ] Check calendar event has ✅ prefix
- [ ] Sync 3 tasks at once
- [ ] Check all 3 appear in calendar
- [ ] Sign out and sign back in
- [ ] Check tasks still synced

---

## Visual Timeline

```
Your App                        Google Calendar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━
Task Created
"Job interview at 9am"    →    

User clicks "Sync"        →    Creating event...

                          →    ✅ Event created!
                               🔴 9:00 AM - 10:00 AM
                               Job interview

User marks complete       →    Updating event...

                          →    ✅ Event updated!
                               ✅ 9:00 AM - 10:00 AM
                               ✅ Job interview
```

---

## Troubleshooting Examples

### Problem: Events created at wrong time
```
Input: "due": "09:00"
Expected: 9:00 AM today
Actual: 9:00 AM tomorrow

Why: Clock already passed 9 AM today
Fix: Check created_at date or manually adjust
```

### Problem: Can't sign in
```
Error: "Unauthorized"

Check:
1. Client ID is correct? ✓
2. localhost:3000 in authorized origins? ✓
3. Email in test users? ✗ <- Add your email!
```

### Problem: Events not appearing
```
Sync says "Success" but no events

Check:
1. Open calendar.google.com
2. Check you're viewing the right account
3. Check "primary" calendar is visible
4. Try refreshing the calendar page
```

---

This guide shows exactly how your JSON format becomes beautiful Google Calendar events! 🎨
