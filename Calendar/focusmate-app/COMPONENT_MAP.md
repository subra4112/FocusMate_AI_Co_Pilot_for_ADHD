# 🗺️ Component Map - How Everything Connects

## App Structure Flow

```
App.jsx (Main Container)
├── Router (React Router)
│   ├── Route "/" → HomePage
│   ├── Route "/calendar" → CalendarPage
│   ├── Route "/tasks" → TasksPage
│   └── Route "/plan" → PlanMyDayPage
└── BottomNav (Always visible)
```

## Component Details

### 🏠 App.jsx (Root Component)
**Purpose:** Main application container  
**State:** 
- `tasks` - Array of all task objects
- `setTasks` - Function to update tasks

**Passes to children:**
- HomePage: `tasks`, `setTasks`
- CalendarPage: `tasks`, `setTasks`
- TasksPage: `tasks`, `setTasks`
- PlanMyDayPage: `tasks`, `setTasks`

**Key Features:**
- Loads tasks from localStorage on mount
- Saves tasks to localStorage on change
- Provides sample tasks as initial data

---

### 🎙️ HomePage.jsx
**Purpose:** Voice input and dashboard  
**Props:** `tasks`, `setTasks`  
**State:** `isListening` - Boolean for mic status

**What it shows:**
- Big microphone button
- Quick stats (active/completed/high priority)
- Recent 3 tasks preview
- Add sample task button

**User Actions:**
- Click mic → (Ready for voice input)
- Click "Add Sample Task" → Creates new task

---

### 📅 CalendarPage.jsx
**Purpose:** Calendar view of tasks  
**Props:** `tasks`, `setTasks`  
**State:** `selectedTask` - Currently selected task for modal

**Components Used:**
- `<TaskCalendar>` - The calendar component

**What it shows:**
- Full calendar with task events
- Task detail modal on click
- Complete/incomplete button

**User Actions:**
- Click task → Opens detail modal
- Click "Mark Complete" → Toggles task completion

---

### ✅ TasksPage.jsx
**Purpose:** List view of all tasks  
**Props:** `tasks`, `setTasks`  
**State:** `filter` - Current filter (all/active/completed)

**Components Used:**
- `<TaskList>` - The task list component

**What it shows:**
- Filter tabs (All/Active/Completed)
- Task summary counts
- Filtered list of tasks

**User Actions:**
- Click filter tab → Changes visible tasks
- Click checkbox → Marks task complete
- Click task → Shows task details

---

### 🤖 PlanMyDayPage.jsx
**Purpose:** AI-powered day planning  
**Props:** `tasks`, `setTasks`

**Components Used:**
- `<DayPlanner>` - The planning component

**What it shows:**
- Day planner with schedule generation
- Work hours configuration
- Time blocks with tasks and breaks

**User Actions:**
- Set work hours → Changes available time
- Click "Generate Schedule" → Creates time blocks
- View scheduled tasks → See time allocation

---

## 🧩 Reusable Components

### BottomNav.jsx
**Purpose:** Navigation bar  
**Props:** None (uses React Router hooks)

**What it does:**
- Shows 4 navigation buttons
- Highlights active page
- Navigates between screens

**Icons:**
- Mic → HomePage
- Calendar → CalendarPage
- CheckSquare → TasksPage
- Sparkles → PlanMyDayPage

---

### TaskCalendar.jsx
**Purpose:** Calendar visualization  
**Props:** 
- `tasks` - Array of task objects
- `onSelectTask` - Callback when task clicked

**Library:** react-big-calendar

**What it does:**
- Converts tasks to calendar events
- Colors by priority (red/yellow/green)
- Shows completed tasks as faded
- Supports week/month/day/agenda views

**Event styling logic:**
```javascript
High priority → Red (#dc3545)
Medium priority → Yellow (#ffc107)
Low priority → Green (#28a745)
Completed → Gray (#6c757d) + faded
```

---

### TaskList.jsx
**Purpose:** List of tasks  
**Props:**
- `tasks` - Array of task objects
- `onToggleComplete` - Callback for checkbox
- `onSelectTask` - Callback for task click

**What it does:**
- Sorts tasks (incomplete first, then by priority/due date)
- Shows priority icons
- Formats due dates ("Today", "Tomorrow", etc)
- Shows estimated duration

**Sorting logic:**
1. Incomplete tasks first
2. Then by priority (high → medium → low)
3. Then by due date (soonest first)

---

### DayPlanner.jsx
**Purpose:** AI day scheduling  
**Props:**
- `tasks` - Array of task objects
- `onUpdateSchedule` - Callback with schedule

**State:**
- `schedule` - Array of time blocks
- `workStartTime` - Work day start
- `workEndTime` - Work day end

**What it does:**
- Filters incomplete tasks
- Sorts by urgency (due date + priority)
- Creates time blocks within work hours
- Adds 10-min breaks every 90 mins
- Shows progress stats

**Algorithm:**
```javascript
1. Get incomplete tasks
2. Sort by: days_until_due + (priority * 10)
3. Start at workStartTime
4. For each task:
   - Check if it fits before workEndTime
   - Add task block (estimated_minutes)
   - Add break block every 2 tasks
5. Return schedule array
```

---

## 📊 Data Flow

### Task Creation
```
User Action (HomePage)
    ↓
setTasks([...tasks, newTask])
    ↓
App.jsx updates state
    ↓
localStorage.setItem('focusmate-tasks', tasks)
    ↓
All components re-render with new data
```

### Task Completion
```
User clicks checkbox (TaskList)
    ↓
onToggleComplete(taskId) called
    ↓
Parent (TasksPage) updates tasks
    ↓
setTasks(tasks.map(...))
    ↓
App.jsx saves to localStorage
    ↓
TaskList re-renders
```

### Day Planning
```
User clicks "Generate Schedule" (DayPlanner)
    ↓
generateSchedule() runs algorithm
    ↓
Creates time blocks array
    ↓
onUpdateSchedule(blocks) called
    ↓
Parent (PlanMyDayPage) updates tasks
    ↓
Tasks get scheduled_start/end times
    ↓
Calendar shows scheduled times
```

---

## 🎨 Styling Architecture

### Global Styles (index.css)
- CSS variables
- Root font settings
- Dark mode colors

### App Styles (App.css)
- Layout structure
- Page container
- Common elements

### Component Styles
Each component has its own CSS:
- BottomNav.css → Navigation
- TaskCalendar.css → Calendar theme
- TaskList.css → Task items
- DayPlanner.css → Schedule blocks
- HomePage.css → Home screen
- CalendarPage.css → Calendar page
- TasksPage.css → Tasks page
- PlanMyDayPage.css → Planner page

**Color Scheme:**
```css
Background: #0a0e27 (dark blue)
Cards: #1a1f3a (lighter blue)
Borders: #2a2f4a (even lighter)
Text: #ffffff (white)
Muted text: #8892b0 (gray-blue)
Accent: #64ffda (teal)
Gradient: #667eea → #764ba2 (purple)
```

---

## 🔄 State Management

### App-level State
```javascript
const [tasks, setTasks] = useState([...]);
```
- Stored in App.jsx
- Passed to all pages
- Persisted in localStorage

### Page-level State
Each page can have its own state:
- HomePage: `isListening`
- CalendarPage: `selectedTask`
- TasksPage: `filter`
- PlanMyDayPage: (managed by DayPlanner)

### Component-level State
- DayPlanner: `schedule`, `workStartTime`, `workEndTime`
- No other components need internal state

---

## 🚀 Adding New Features

### Add a new page:
1. Create `src/pages/NewPage.jsx`
2. Create `src/pages/NewPage.css`
3. Add route in `App.jsx`:
   ```javascript
   <Route path="/new" element={<NewPage tasks={tasks} setTasks={setTasks} />} />
   ```
4. Add button in `BottomNav.jsx`

### Add a new component:
1. Create `src/components/NewComponent.jsx`
2. Create `src/components/NewComponent.css`
3. Import and use in any page:
   ```javascript
   import NewComponent from '../components/NewComponent';
   ```

### Modify task structure:
1. Update sample data in `App.jsx`
2. Update component logic that uses tasks
3. No database changes needed (it's JSON!)

---

## 📱 Screen Navigation

```
┌─────────────────────────────────┐
│         FocusMate App           │
│  ┌──────────────────────────┐  │
│  │                          │  │
│  │    Current Page          │  │
│  │    (HomePage,            │  │
│  │     CalendarPage,        │  │
│  │     TasksPage, or        │  │
│  │     PlanMyDayPage)       │  │
│  │                          │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌────┬────┬────┬────┐         │
│  │ 🎙️ │ 📅 │ ✅ │ ✨ │ ← BottomNav
│  └────┴────┴────┴────┘         │
└─────────────────────────────────┘
```

User can tap any icon to switch screens instantly!

---

This map should help you understand how all the pieces fit together. 🧩
