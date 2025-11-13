import React, { useMemo } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './TaskCalendar.css';

const localizer = momentLocalizer(moment);

function TaskCalendar({ tasks, onSelectTask }) {
  // Convert tasks to calendar events
  const events = useMemo(() => {
    return tasks.map(task => {
      const startTime = task.scheduled_start || task.due_datetime;
      const endTime = task.scheduled_end || 
        moment(startTime).add(task.estimated_minutes || 30, 'minutes').toISOString();

      return {
        id: task.id,
        title: task.action,
        start: new Date(startTime),
        end: new Date(endTime),
        resource: task,
        allDay: !task.due_time
      };
    });
  }, [tasks]);

  // Custom styling based on priority and completion
  const eventStyleGetter = (event) => {
    const task = event.resource;
    let backgroundColor = '#3174ad';
    
    if (task.completed) {
      backgroundColor = '#6c757d';
    } else if (task.priority === 'high') {
      backgroundColor = '#dc3545';
    } else if (task.priority === 'medium') {
      backgroundColor = '#ffc107';
    } else {
      backgroundColor = '#28a745';
    }
    
    return {
      style: {
        backgroundColor,
        opacity: task.completed ? 0.5 : 1,
        textDecoration: task.completed ? 'line-through' : 'none',
        borderRadius: '8px',
        border: 'none',
        padding: '4px 8px',
        color: '#ffffff',
        fontSize: '13px'
      }
    };
  };

  return (
    <div className="calendar-container">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        onSelectEvent={(event) => onSelectTask && onSelectTask(event.resource)}
        eventPropGetter={eventStyleGetter}
        views={['month', 'week', 'day', 'agenda']}
        defaultView="week"
        style={{ height: '100%' }}
        popup
      />
    </div>
  );
}

export default TaskCalendar;
