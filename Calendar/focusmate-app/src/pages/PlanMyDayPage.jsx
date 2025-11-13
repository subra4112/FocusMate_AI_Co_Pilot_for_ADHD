import React from 'react';
import DayPlanner from '../components/DayPlanner';
import './PlanMyDayPage.css';

function PlanMyDayPage({ tasks, setTasks }) {
  const handleUpdateSchedule = (schedule) => {
    // Update tasks with scheduled times
    const updatedTasks = tasks.map(task => {
      const block = schedule.find(b => b.taskId === task.id);
      if (block) {
        return {
          ...task,
          scheduled_start: block.start,
          scheduled_end: block.end
        };
      }
      return task;
    });
    
    setTasks(updatedTasks);
  };

  return (
    <div className="page plan-page">
      <DayPlanner 
        tasks={tasks}
        onUpdateSchedule={handleUpdateSchedule}
      />
    </div>
  );
}

export default PlanMyDayPage;
