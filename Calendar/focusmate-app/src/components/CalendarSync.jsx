import React, { useState } from 'react';
import { useGoogleCalendar } from '../hooks/useGoogleCalendar';
import { Calendar, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import './CalendarSync.css';

function CalendarSync({ tasks, onTasksUpdate }) {
  const { isSignedIn, isLoading, error, signIn, signOut, syncTasks, createEvent } = useGoogleCalendar();
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null);

  const handleSignIn = async () => {
    try {
      await signIn();
    } catch (err) {
      console.error('Sign in failed:', err);
    }
  };

  const handleSyncAll = async () => {
    try {
      setSyncing(true);
      setSyncResult(null);
      
      // Sync all incomplete tasks
      const results = await syncTasks(tasks);
      
      // Update tasks with calendar event IDs
      const updatedTasks = tasks.map(task => {
        const result = results.find(r => r.taskId === task.id);
        if (result && result.success) {
          return { ...task, calendar_event_id: result.eventId };
        }
        return task;
      });
      
      onTasksUpdate(updatedTasks);
      setSyncResult(results);
      setSyncing(false);
    } catch (err) {
      console.error('Sync failed:', err);
      setSyncing(false);
    }
  };

  const handleSyncSingle = async (task) => {
    try {
      const eventId = await createEvent(task);
      
      // Update this task with the event ID
      const updatedTasks = tasks.map(t => 
        t.id === task.id ? { ...t, calendar_event_id: eventId } : t
      );
      
      onTasksUpdate(updatedTasks);
      
      alert(`✅ "${task.action}" added to Google Calendar!`);
    } catch (err) {
      console.error('Failed to create event:', err);
      alert(`❌ Failed to add task to calendar: ${err.message}`);
    }
  };

  if (isLoading) {
    return (
      <div className="calendar-sync loading">
        <Loader className="spin" size={24} />
        <span>Loading Google Calendar...</span>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="calendar-sync">
        <div className="sync-prompt">
          <Calendar size={48} />
          <h3>Connect Google Calendar</h3>
          <p>Sync your tasks to Google Calendar to never miss a deadline</p>
          <button className="sign-in-btn" onClick={handleSignIn}>
            <Calendar size={20} />
            Sign in with Google
          </button>
          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="calendar-sync">
      <div className="sync-header">
        <div className="sync-status">
          <CheckCircle size={20} color="#28a745" />
          <span>Connected to Google Calendar</span>
        </div>
        <button className="sign-out-btn" onClick={signOut}>
          Sign Out
        </button>
      </div>

      <div className="sync-actions">
        <button 
          className="sync-all-btn" 
          onClick={handleSyncAll}
          disabled={syncing || tasks.filter(t => !t.completed).length === 0}
        >
          {syncing ? (
            <>
              <Loader className="spin" size={20} />
              Syncing...
            </>
          ) : (
            <>
              <Calendar size={20} />
              Sync All Tasks ({tasks.filter(t => !t.completed).length})
            </>
          )}
        </button>
      </div>

      {syncResult && (
        <div className="sync-result">
          <h4>Sync Complete!</h4>
          <div className="result-stats">
            <div className="stat success">
              <CheckCircle size={16} />
              <span>{syncResult.filter(r => r.success).length} synced</span>
            </div>
            {syncResult.filter(r => !r.success).length > 0 && (
              <div className="stat error">
                <AlertCircle size={16} />
                <span>{syncResult.filter(r => !r.success).length} failed</span>
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <div className="task-sync-list">
        <h4>Quick Sync Individual Tasks</h4>
        {tasks.filter(t => !t.completed && !t.calendar_event_id).slice(0, 5).map(task => (
          <div key={task.id} className="task-sync-item">
            <div className="task-info">
              <span className={`priority-dot priority-${task.priority}`}></span>
              <span className="task-name">{task.action}</span>
            </div>
            <button 
              className="sync-task-btn"
              onClick={() => handleSyncSingle(task)}
            >
              <Calendar size={16} />
              Add to Calendar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CalendarSync;
