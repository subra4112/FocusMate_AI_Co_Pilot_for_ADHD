import React, { useState } from 'react';
import TaskList from '../components/TaskList';
import { Filter } from 'lucide-react';
import './TasksPage.css';
import CalendarSync from '../components/CalendarSync';


function TasksPage({ tasks, setTasks }) {
  const [filter, setFilter] = useState('all'); // 'all', 'active', 'completed'

  const toggleComplete = (taskId) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed, status: task.completed ? 'todo' : 'done' }
        : task
    ));
  };

  const handleSelectTask = (task) => {
    console.log('Selected task:', task);
    // You can open a modal or navigate to detail page
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  const activeTasks = tasks.filter(t => !t.completed).length;
  const completedTasks = tasks.filter(t => t.completed).length;

  return (
    <div className="page tasks-page">
      <header className="page-header">
        <div>
          <h1>My Tasks</h1>
          <p className="tasks-summary">
            {activeTasks} active · {completedTasks} completed
          </p>
        </div>
      </header>

       <CalendarSync tasks={tasks} onTasksUpdate={setTasks} />

      <div className="filter-tabs">
        <button 
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({tasks.length})
        </button>
        <button 
          className={`filter-tab ${filter === 'active' ? 'active' : ''}`}
          onClick={() => setFilter('active')}
        >
          Active ({activeTasks})
        </button>
        <button 
          className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
          onClick={() => setFilter('completed')}
        >
          Completed ({completedTasks})
        </button>
      </div>
      
      <TaskList 
        tasks={filteredTasks}
        onToggleComplete={toggleComplete}
        onSelectTask={handleSelectTask}
      />
    </div>
  );
}

export default TasksPage;
