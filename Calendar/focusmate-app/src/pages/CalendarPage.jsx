import React, { useState, useEffect } from 'react';
import TaskCalendar from '../components/TaskCalendar';
import { X, RefreshCw, Calendar as CalendarIcon } from 'lucide-react';
import { useGoogleCalendar } from '../hooks/useGoogleCalendar';
import moment from 'moment';
import './CalendarPage.css';

function CalendarPage({ tasks, setTasks }) {
  const [selectedTask, setSelectedTask] = useState(null);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [allTasks, setAllTasks] = useState(tasks);
  const [loading, setLoading] = useState(false);
  const { isSignedIn, signIn, fetchEvents, convertEventToTask } = useGoogleCalendar();

  // Fetch Google Calendar events when signed in
  useEffect(() => {
    if (isSignedIn) {
      fetchCalendarEvents();
    } else {
      // Only show local tasks if not signed in
      setAllTasks(tasks);
    }
  }, [isSignedIn, tasks]);

  const fetchCalendarEvents = async () => {
    try {
      setLoading(true);
      
      // Get events from 1 month ago to 3 months in future
      const startDate = moment().subtract(1, 'month').toDate();
      const endDate = moment().add(3, 'months').toDate();
      
      const events = await fetchEvents(startDate, endDate);
      
      // Convert Google Calendar events to task format
      const convertedTasks = events.map(event => convertEventToTask(event));
      
      // Merge with local tasks (avoid duplicates by calendar_event_id)
      const localTaskIds = new Set(tasks.map(t => t.calendar_event_id).filter(Boolean));
      const newCalendarTasks = convertedTasks.filter(t => !localTaskIds.has(t.id));
      
      // Combine local tasks with calendar imports
      const combined = [...tasks, ...newCalendarTasks];
      
      setAllTasks(combined);
      setCalendarEvents(events);
      setLoading(false);
      
      console.log(`✅ Loaded ${events.length} events from Google Calendar`);
    } catch (error) {
      console.error('Failed to fetch calendar events:', error);
      setLoading(false);
      // Fall back to showing only local tasks
      setAllTasks(tasks);
    }
  };

  const handleToggleComplete = (taskId) => {
    const updatedTasks = allTasks.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed, status: task.completed ? 'todo' : 'done' }
        : task
    );
    setAllTasks(updatedTasks);
    
    // Update the main tasks state if it's a local task
    if (tasks.find(t => t.id === taskId)) {
      setTasks(tasks.map(task => 
        task.id === taskId 
          ? { ...task, completed: !task.completed, status: task.completed ? 'todo' : 'done' }
          : task
      ));
    }
  };

  const handleRefresh = () => {
    if (isSignedIn) {
      fetchCalendarEvents();
    }
  };

  return (
    <div className="page calendar-page">
      <header className="page-header">
        <div>
          <h1>Schedule</h1>
          <p className="calendar-subtitle">
            {isSignedIn ? (
              <>✅ Showing {allTasks.length} events (Local + Google Calendar)</>
            ) : (
              <>📅 Showing {tasks.length} local tasks</>
            )}
          </p>
        </div>
        <div className="calendar-actions">
          {!isSignedIn ? (
            <button className="connect-calendar-btn" onClick={signIn}>
              <CalendarIcon size={16} />
              Connect Calendar
            </button>
          ) : (
            <button 
              className="refresh-btn" 
              onClick={handleRefresh}
              disabled={loading}
            >
              <RefreshCw size={16} className={loading ? 'spinning' : ''} />
              Refresh
            </button>
          )}
        </div>
      </header>
      
      <TaskCalendar 
        tasks={allTasks} 
        onSelectTask={setSelectedTask}
      />

      {selectedTask && (
        <div className="task-detail-modal" onClick={() => setSelectedTask(null)}>
          <div className="task-detail-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedTask(null)}>
              <X size={24} />
            </button>
            
            <h2>{selectedTask.action}</h2>
            
            <div className="task-detail-info">
              <div className="info-row">
                <span className="info-label">Priority:</span>
                <span className={`priority-badge priority-${selectedTask.priority}`}>
                  {selectedTask.priority}
                </span>
              </div>
              
              <div className="info-row">
                <span className="info-label">Duration:</span>
                <span>{selectedTask.estimated_minutes || 30} minutes</span>
              </div>
              
              <div className="info-row">
                <span className="info-label">Status:</span>
                <span className={selectedTask.completed ? 'completed-text' : 'pending-text'}>
                  {selectedTask.completed ? 'Completed' : 'Pending'}
                </span>
              </div>

              {selectedTask.transcript && (
                <div className="info-row">
                  <span className="info-label">From Voice:</span>
                  <span className="transcript-text">"{selectedTask.transcript.substring(0, 100)}..."</span>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button 
                className="complete-btn"
                onClick={() => {
                  handleToggleComplete(selectedTask.id);
                  setSelectedTask(null);
                }}
              >
                {selectedTask.completed ? 'Mark Incomplete' : 'Mark Complete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CalendarPage;
