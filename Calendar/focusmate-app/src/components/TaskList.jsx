import React from 'react';
import { CheckCircle, Circle, Clock, AlertCircle } from 'lucide-react';
import moment from 'moment';
import './TaskList.css';

function TaskList({ tasks, onToggleComplete, onSelectTask }) {
  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <AlertCircle color="#dc3545" size={20} />;
    if (priority === 'medium') return <Clock color="#ffc107" size={20} />;
    return <Clock color="#28a745" size={20} />;
  };

  const formatDueDate = (dueDateTime) => {
    if (!dueDateTime) return 'No due date';
    const date = moment(dueDateTime);
    const today = moment().startOf('day');
    const tomorrow = moment().add(1, 'day').startOf('day');

    if (date.isSame(today, 'day')) return 'Today at ' + date.format('h:mm A');
    if (date.isSame(tomorrow, 'day')) return 'Tomorrow at ' + date.format('h:mm A');
    return date.format('MMM D, h:mm A');
  };

  const sortedTasks = [...tasks].sort((a, b) => {
    // Completed tasks go to bottom
    if (a.completed !== b.completed) return a.completed ? 1 : -1;
    
    // Sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;
    
    // Sort by due date
    return moment(a.due_datetime).diff(moment(b.due_datetime));
  });

  if (tasks.length === 0) {
    return (
      <div className="empty-tasks">
        <CheckCircle size={48} color="#64ffda" />
        <p>No tasks yet. Add some from the Voice screen!</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {sortedTasks.map(task => (
        <div 
          key={task.id} 
          className={`task-item ${task.completed ? 'completed' : ''} priority-${task.priority}`}
          onClick={() => onSelectTask && onSelectTask(task)}
        >
          <button 
            className="task-checkbox"
            onClick={(e) => {
              e.stopPropagation();
              onToggleComplete(task.id);
            }}
          >
            {task.completed ? 
              <CheckCircle color="#28a745" size={24} /> : 
              <Circle size={24} />
            }
          </button>
          
          <div className="task-content">
            <h3 className="task-title">{task.action}</h3>
            <div className="task-meta">
              {getPriorityIcon(task.priority)}
              <span className="task-due">{formatDueDate(task.due_datetime)}</span>
              {task.estimated_minutes && (
                <span className="task-duration">{task.estimated_minutes} min</span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default TaskList;
