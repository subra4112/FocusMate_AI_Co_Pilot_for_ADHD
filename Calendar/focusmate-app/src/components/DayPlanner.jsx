import React, { useState } from 'react';
import { Sparkles, Clock, Coffee, Star } from 'lucide-react';
import moment from 'moment';
import './DayPlanner.css';

function DayPlanner({ tasks, onUpdateSchedule }) {
  const [schedule, setSchedule] = useState([]);
  const [workStartTime, setWorkStartTime] = useState('09:00');
  const [workEndTime, setWorkEndTime] = useState('18:00');

  const generateSchedule = () => {
    // Filter incomplete tasks
    const incompleteTasks = tasks.filter(t => !t.completed);
    
    // Sort by urgency and priority
    const sortedTasks = [...incompleteTasks].sort((a, b) => {
      const aDays = moment(a.due_datetime).diff(moment(), 'days');
      const bDays = moment(b.due_datetime).diff(moment(), 'days');
      
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const aScore = aDays + priorityOrder[a.priority] * 10;
      const bScore = bDays + priorityOrder[b.priority] * 10;
      
      return aScore - bScore;
    });

    // Generate time blocks
    const blocks = [];
    const today = moment().format('YYYY-MM-DD');
    let currentTime = moment(`${today}T${workStartTime}`);
    const endTime = moment(`${today}T${workEndTime}`);

    sortedTasks.forEach((task, index) => {
      // Add break after every 90 minutes of work
      if (index > 0 && index % 2 === 0) {
        blocks.push({
          id: `break-${index}`,
          type: 'break',
          label: 'Take a break 🧘',
          start: currentTime.toISOString(),
          end: currentTime.add(10, 'minutes').toISOString(),
          icon: 'coffee'
        });
      }

      const duration = task.estimated_minutes || 30;
      
      // Check if we have time left today
      if (currentTime.clone().add(duration, 'minutes').isAfter(endTime)) {
        return; // Skip tasks that don't fit
      }

      const blockStart = currentTime.toISOString();
      const blockEnd = currentTime.add(duration, 'minutes').toISOString();

      blocks.push({
        id: task.id,
        type: 'task',
        taskId: task.id,
        label: task.action,
        start: blockStart,
        end: blockEnd,
        priority: task.priority,
        icon: 'task'
      });
    });

    setSchedule(blocks);
    
    // Update tasks with scheduled times
    if (onUpdateSchedule) {
      onUpdateSchedule(blocks);
    }
  };

  const getProgressStats = () => {
    const totalTasks = tasks.filter(t => !t.completed).length;
    const scheduledTasks = schedule.filter(b => b.type === 'task').length;
    const percentage = totalTasks > 0 ? Math.round((scheduledTasks / totalTasks) * 100) : 0;
    
    return { totalTasks, scheduledTasks, percentage };
  };

  const stats = getProgressStats();

  const renderTimeBlock = (block) => {
    const startTime = moment(block.start).format('h:mm A');
    const endTime = moment(block.end).format('h:mm A');
    
    return (
      <div 
        key={block.id} 
        className={`time-block ${block.type} priority-${block.priority}`}
      >
        <div className="time-block-time">
          <Clock size={16} />
          <span>{startTime} - {endTime}</span>
        </div>
        <div className="time-block-label">
          {block.type === 'break' ? <Coffee size={20} /> : <Star size={20} />}
          {block.label}
        </div>
      </div>
    );
  };

  return (
    <div className="day-planner">
      <div className="planner-header">
        <div>
          <h2>Plan My Day</h2>
          {schedule.length > 0 && (
            <p className="planner-subtitle">
              {stats.scheduledTasks} of {stats.totalTasks} tasks scheduled ({stats.percentage}%)
            </p>
          )}
        </div>
        <button className="generate-btn" onClick={generateSchedule}>
          <Sparkles size={20} />
          Generate Schedule
        </button>
      </div>

      <div className="work-hours">
        <label>
          <span>Work Start:</span>
          <input 
            type="time" 
            value={workStartTime} 
            onChange={(e) => setWorkStartTime(e.target.value)}
          />
        </label>
        <label>
          <span>Work End:</span>
          <input 
            type="time" 
            value={workEndTime} 
            onChange={(e) => setWorkEndTime(e.target.value)}
          />
        </label>
      </div>

      <div className="schedule-timeline">
        {schedule.length === 0 ? (
          <div className="empty-schedule">
            <Sparkles size={48} />
            <p>Click "Generate Schedule" to plan your day</p>
            <p className="empty-schedule-hint">
              AI will organize your tasks based on priority and due dates
            </p>
          </div>
        ) : (
          <>
            <div className="schedule-summary">
              <div className="summary-card">
                <Clock size={24} />
                <div>
                  <span className="summary-label">Total Time</span>
                  <span className="summary-value">
                    {Math.round(moment(schedule[schedule.length - 1].end).diff(moment(schedule[0].start), 'minutes') / 60 * 10) / 10}h
                  </span>
                </div>
              </div>
              <div className="summary-card">
                <Coffee size={24} />
                <div>
                  <span className="summary-label">Breaks</span>
                  <span className="summary-value">
                    {schedule.filter(b => b.type === 'break').length}
                  </span>
                </div>
              </div>
            </div>
            {schedule.map(renderTimeBlock)}
          </>
        )}
      </div>
    </div>
  );
}

export default DayPlanner;
