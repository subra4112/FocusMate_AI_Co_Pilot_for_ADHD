import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CalendarPage from './pages/CalendarPage';
import TasksPage from './pages/TasksPage';
import PlanMyDayPage from './pages/PlanMyDayPage';
import BottomNav from './components/BottomNav';
import './App.css';

function App() {
  // Initialize with sample tasks from your JSON
  const [tasks, setTasks] = useState([
    {
      "id": "20251109_141643_947332",
      "created_at": "2025-11-09T14:16:43.947332",
      "action": "Get groceries",
      "due_date": "2025-11-09",
      "due_time": "15:00",
      "due_datetime": "2025-11-09T15:00:00",
      "estimated_minutes": 30,
      "calendar_event_id": null,  // Filled by Google Calendar sync
      "scheduled_start": null,
      "scheduled_end": null,
      "priority": "medium",
      "confidence": 0.9,
      "rationale": "Extracted from multi-task analysis",
      "transcript": "Uh, what do I do now? Do I have to do this? Today, I have a task at 8:00 where I have to finish an assignment. Then, I have to go to get some groceries. Then, I have a really good job, uh, interview tomorrow ... at 9:00.",
      "completed": false,
      "status": "todo"
    },
    {
      "id": "20251109_141643_947831",
      "created_at": "2025-11-09T14:16:43.947831",
      "action": "Prepare for job interview",
      "due_date": "2025-11-10",
      "due_time": "09:00",
      "due_datetime": "2025-11-10T09:00:00",
      "estimated_minutes": 60,
      "calendar_event_id": null,
      "scheduled_start": null,
      "scheduled_end": null,
      "priority": "high",
      "confidence": 0.9,
      "rationale": "Extracted from multi-task analysis",
      "transcript": "Uh, what do I do now? Do I have to do this? Today, I have a task at 8:00 where I have to finish an assignment. Then, I have to go to get some groceries. Then, I have a really good job, uh, interview tomorrow ... at 9:00.",
      "completed": false,
      "status": "todo"
    },
    {
      "id": "20251109_141643_947833",
      "created_at": "2025-11-09T14:16:43.947833",
      "action": "Finish assignment",
      "due_date": "2025-11-09",
      "due_time": "20:00",
      "due_datetime": "2025-11-09T20:00:00",
      "estimated_minutes": 90,
      "calendar_event_id": null,
      "scheduled_start": null,
      "scheduled_end": null,
      "priority": "high",
      "confidence": 0.95,
      "rationale": "Extracted from multi-task analysis",
      "transcript": "Today, I have a task at 8:00 where I have to finish an assignment.",
      "completed": false,
      "status": "todo"
    }
  ]);

  // Load tasks from localStorage on mount
  useEffect(() => {
    const savedTasks = localStorage.getItem('focusmate-tasks');
    if (savedTasks) {
      setTasks(JSON.parse(savedTasks));
    }
  }, []);

  // Save tasks to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('focusmate-tasks', JSON.stringify(tasks));
  }, [tasks]);

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<HomePage tasks={tasks} setTasks={setTasks} />} />
          <Route path="/calendar" element={<CalendarPage tasks={tasks} setTasks={setTasks} />} />
          <Route path="/tasks" element={<TasksPage tasks={tasks} setTasks={setTasks} />} />
          <Route path="/plan" element={<PlanMyDayPage tasks={tasks} setTasks={setTasks} />} />
        </Routes>
        <BottomNav />
      </div>
    </Router>
  );
}

export default App;
