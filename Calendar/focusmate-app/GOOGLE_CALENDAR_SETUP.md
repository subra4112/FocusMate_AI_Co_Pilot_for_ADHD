# 📅 Google Calendar Integration Guide

## Overview

Your FocusMate app now includes Google Calendar integration! This allows you to:
- ✅ Sync tasks to your Google Calendar
- ✅ Auto-create calendar events with reminders
- ✅ Color-code by priority (Red/Yellow/Green)
- ✅ Mark events complete with ✅ emoji
- ✅ Include voice transcripts in event descriptions

## 🎯 Your Task Format - Perfect for Calendar!

Your JSON format works great with Google Calendar:

```json
{
  "id": "20251109_141643_947831",
  "created_at": "2025-11-09T14:16:43.947831",
  "action": "Prepare for job interview",
  "due": "09:00",                    // ← We use this for the time!
  "priority": "high",                 // ← Color codes the event
  "confidence": 0.9,
  "rationale": "Extracted from multi-task analysis",
  "transcript": "...",                // ← Added to event description
  "completed": false
}
```

### How We Handle Your Format:
- `due: "09:00"` → Creates event at 9:00 AM today
- `created_at` → Used to determine the date
- `priority` → Calendar color (high=red, medium=yellow, low=green)
- `transcript` → Shown in event description
- Duration: high priority = 60 mins, medium = 45 mins, low = 30 mins

---

## 🚀 Setup Steps

### Step 1: Get Google Calendar API Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project**
   - Click "Select a project" → "New Project"
   - Name it "FocusMate" → Click "Create"

3. **Enable Google Calendar API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click on it → Click "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Click "Configure Consent Screen"
   
5. **Configure OAuth Consent Screen**
   - User Type: External → Click "Create"
   - App name: "FocusMate"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Click "Save and Continue" (skip for now)
   - Test users: Add your Gmail address
   - Click "Save and Continue"

6. **Create OAuth Client ID**
   - Application type: "Web application"
   - Name: "FocusMate Web Client"
   - Authorized JavaScript origins:
     - http://localhost:3000
     - http://localhost:5173 (Vite dev server)
   - Authorized redirect URIs: (leave empty for now)
   - Click "Create"

7. **Copy Your Credentials**
   - You'll see a popup with:
     - Client ID (looks like: xxxxx.apps.googleusercontent.com)
     - Client Secret (you don't need this for web apps)
   - **SAVE THE CLIENT ID!**

8. **Create API Key**
   - Go back to "Credentials"
   - Click "Create Credentials" → "API key"
   - Copy the API key
   - Click "Restrict Key"
   - API restrictions: Select "Google Calendar API"
   - Click "Save"

---

### Step 2: Add Credentials to Your App

1. **Open the file:**
   ```
   src/services/googleCalendar.js
   ```

2. **Replace these lines** (around line 7-8):
   ```javascript
   this.CLIENT_ID = 'YOUR_CLIENT_ID.apps.googleusercontent.com';
   this.API_KEY = 'YOUR_API_KEY';
   ```

   **With your actual credentials:**
   ```javascript
   this.CLIENT_ID = '123456789-abcdefg.apps.googleusercontent.com';  // Your real Client ID
   this.API_KEY = 'AIzaSyABC123_YourRealAPIKey';  // Your real API Key
   ```

3. **Save the file**

---

### Step 3: Add CalendarSync to Your App

1. **Open:** `src/pages/TasksPage.jsx`

2. **Import the component** (add at the top):
   ```javascript
   import CalendarSync from '../components/CalendarSync';
   ```

3. **Add it to the page** (after the page header):
   ```javascript
   <div className="page tasks-page">
     <header className="page-header">
       {/* ... existing header ... */}
     </header>

     {/* Add this: */}
     <CalendarSync tasks={tasks} onTasksUpdate={setTasks} />

     {/* ... rest of the page ... */}
   </div>
   ```

---

## 🎨 How It Looks

### Before Sign-In:
```
┌─────────────────────────────┐
│   Connect Google Calendar   │
│                             │
│   📅 (Calendar Icon)        │
│                             │
│   Sync your tasks to        │
│   Google Calendar to never  │
│   miss a deadline           │
│                             │
│  [Sign in with Google]      │
└─────────────────────────────┘
```

### After Sign-In:
```
┌─────────────────────────────┐
│ ✅ Connected to Google       │
│    Calendar        [Sign Out]│
├─────────────────────────────┤
│ [📅 Sync All Tasks (3)]     │
├─────────────────────────────┤
│ Quick Sync Individual Tasks │
│                             │
│ 🔴 Prepare for interview    │
│                  [Add to Cal]│
│ 🟡 Get groceries            │
│                  [Add to Cal]│
│ 🟢 Finish assignment        │
│                  [Add to Cal]│
└─────────────────────────────┘
```

---

## 💡 Usage Examples

### Example 1: Sync All Tasks

```javascript
// Your task:
{
  "action": "Prepare for job interview",
  "due": "09:00",
  "priority": "high",
  "transcript": "I have a really good job interview tomorrow at 9:00"
}

// Creates Google Calendar Event:
Title: "Prepare for job interview"
Time: Today at 9:00 AM - 10:00 AM (1 hour)
Color: Red (high priority)
Description:
  🎙️ From Voice: "I have a really good job interview tomorrow at 9:00"
  📋 Priority: high
  🤖 Confidence: 90%
  💡 Rationale: Extracted from multi-task analysis
  📱 Created via FocusMate
Reminders: 30 mins before, 10 mins before
```

### Example 2: Mark Task Complete

When you check off a task in FocusMate:
- Calendar event title updates to: "✅ Prepare for job interview"
- Color changes to gray
- Still visible in your calendar history

---

## 🔧 Advanced Features

### Auto-Calculate Event Duration

The service automatically assigns duration based on priority:
```javascript
High priority   → 60 minutes
Medium priority → 45 minutes
Low priority    → 30 minutes
```

### Smart Date Parsing

Handles your `"due": "09:00"` format intelligently:
```javascript
// If task created today at 2 PM
"due": "09:00" → Creates event tomorrow at 9 AM (since 9 AM already passed)

// If task created at 8 AM
"due": "09:00" → Creates event today at 9 AM
```

### Transcript in Description

Your voice transcripts are preserved:
```
Event Description:
🎙️ From Voice: "Uh, what do I do now? I have a task at 8:00..."
📋 Priority: high
🤖 Confidence: 90%
💡 Rationale: Extracted from multi-task analysis
📱 Created via FocusMate
```

---

## 🐛 Troubleshooting

### "Sign in with Google" button doesn't work
- **Check:** Did you add your Client ID and API Key?
- **Check:** Are you running on localhost:3000 or localhost:5173?
- **Fix:** Make sure these URLs are in "Authorized JavaScript origins"

### "Access blocked: FocusMate has not completed verification"
- **Why:** Your app is in testing mode
- **Fix:** Add your email to "Test users" in OAuth consent screen
- **Or:** Use your test Gmail account

### Events created but wrong time
- **Check:** Your timezone in the browser
- **Check:** The `created_at` date in your tasks
- **Fix:** Make sure `created_at` has the correct date

### "API key not valid"
- **Check:** Did you restrict the API key to Google Calendar API?
- **Check:** Is the key copied correctly (no extra spaces)?

### Can't see the sync component
- **Check:** Did you import and add `<CalendarSync>` to TasksPage?
- **Check:** Browser console for errors (F12)

---

## 📊 Task Update Format

After syncing, your tasks will look like this:

```json
{
  "id": "20251109_141643_947831",
  "created_at": "2025-11-09T14:16:43.947831",
  "action": "Prepare for job interview",
  "due": "09:00",
  "priority": "high",
  "confidence": 0.9,
  "rationale": "Extracted from multi-task analysis",
  "transcript": "...",
  "completed": false,
  "calendar_event_id": "abc123xyz456"  // ← Added after sync!
}
```

The `calendar_event_id` lets you:
- Update the event when task changes
- Mark event complete when task is checked
- Delete event when task is deleted

---

## 🎯 Next Steps

### 1. Basic Integration (You are here!)
- [x] Set up Google Calendar API
- [x] Add credentials
- [x] Test sign-in
- [x] Sync a task

### 2. Auto-Sync on Task Creation
Add this to HomePage when creating tasks:
```javascript
const createTask = async (taskData) => {
  // Create task
  const newTask = { ...taskData };
  setTasks([...tasks, newTask]);
  
  // Auto-sync to calendar if signed in
  if (calendarService.isSignedIn()) {
    const eventId = await calendarService.createEventFromTask(newTask);
    newTask.calendar_event_id = eventId;
  }
};
```

### 3. Sync on Task Complete
Add to TaskList checkbox handler:
```javascript
const handleComplete = async (taskId) => {
  const task = tasks.find(t => t.id === taskId);
  
  // Mark complete in app
  task.completed = true;
  setTasks([...tasks]);
  
  // Mark complete in calendar
  if (task.calendar_event_id) {
    await calendarService.markEventCompleted(task.calendar_event_id, task);
  }
};
```

### 4. Delete from Calendar
When deleting tasks:
```javascript
const deleteTask = async (taskId) => {
  const task = tasks.find(t => t.id === taskId);
  
  // Delete from calendar first
  if (task.calendar_event_id) {
    await calendarService.deleteEvent(task.calendar_event_id);
  }
  
  // Then delete from app
  setTasks(tasks.filter(t => t.id !== taskId));
};
```

---

## 🌟 Features Summary

### ✅ What Works Now:
- Manual sync all tasks
- Manual sync individual tasks
- Sign in/out from Google
- Color-coded events by priority
- Voice transcripts in descriptions
- Automatic reminders (30 min, 10 min)
- Mark events complete

### 🔮 Coming Soon:
- Auto-sync on task creation
- Two-way sync (calendar → app)
- Recurring tasks
- Custom durations
- Multiple calendar support

---

## 📝 Testing Checklist

- [ ] Click "Sign in with Google"
- [ ] Authorize FocusMate to access calendar
- [ ] Click "Sync All Tasks"
- [ ] Open Google Calendar (calendar.google.com)
- [ ] See your tasks as events
- [ ] Check event descriptions have transcripts
- [ ] Check colors match priorities
- [ ] Mark a task complete in FocusMate
- [ ] See event updated with ✅ in calendar

---

## 🎓 Learn More

- [Google Calendar API Docs](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 for Web Apps](https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow)
- [React Hooks Guide](https://react.dev/reference/react)

---

**Your tasks are now synced with Google Calendar! 🎉**

No more forgetting important deadlines!
