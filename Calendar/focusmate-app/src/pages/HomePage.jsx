import React, { useState } from 'react';
import { Mic, Plus } from 'lucide-react';
import './HomePage.css';

function HomePage({ tasks, setTasks }) {
  const [isListening, setIsListening] = useState(false);

  const addSampleTask = () => {
    const newTask = {
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
      action: "New task from voice",
      due_date: new Date().toISOString().split('T')[0],
      due_time: "14:00",
      due_datetime: new Date(Date.now() + 3600000).toISOString(), // 1 hour from now
      estimated_minutes: 45,
      calendar_event_id: null,
      scheduled_start: null,
      scheduled_end: null,
      priority: "medium",
      confidence: 0.85,
      rationale: "Added via voice interface",
      transcript: "Sample voice input",
      completed: false,
      status: "todo"
    };

    setTasks([...tasks, newTask]);
  };

  const handleMicClick = () => {
    setIsListening(!isListening);
    // In real app, this would trigger speech recognition
    alert('Voice recording would start here!\n\nFor demo purposes, click the + button to add a task.');
  };

  return (
    <div className="page home-page">
      <div className="home-header">
        <div className="brand">
          <h1>FocusMate</h1>
          <p className="tagline">Your AI Copilot for ADHD and Anxiety</p>
        </div>
      </div>

      <div className="voice-section">
        <div className="voice-prompt">
          <h2>How are you feeling?</h2>
          <p>Tell me what's on your mind, and I'll help organize your thoughts.</p>
        </div>

        <button 
          className={`mic-button ${isListening ? 'listening' : ''}`}
          onClick={handleMicClick}
        >
          <Mic size={48} />
        </button>

        {isListening && (
          <div className="listening-indicator">
            <div className="pulse"></div>
            <span>Listening...</span>
          </div>
        )}
      </div>

      <div className="quick-stats">
        <div className="stat-card">
          <span className="stat-value">{tasks.filter(t => !t.completed).length}</span>
          <span className="stat-label">Active Tasks</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{tasks.filter(t => t.completed).length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{tasks.filter(t => t.priority === 'high' && !t.completed).length}</span>
          <span className="stat-label">High Priority</span>
        </div>
      </div>

      <div className="quick-actions">
        <button className="action-btn" onClick={addSampleTask}>
          <Plus size={20} />
          Add Sample Task
        </button>
      </div>

      <div className="recent-tasks">
        <h3>Recent Tasks</h3>
        {tasks.slice(-3).reverse().map(task => (
          <div key={task.id} className="task-preview">
            <div className={`priority-dot priority-${task.priority}`}></div>
            <span className="task-preview-text">{task.action}</span>
          </div>
        ))}
        {tasks.length === 0 && (
          <p className="no-tasks">No tasks yet. Start by adding one!</p>
        )}
      </div>
    </div>
  );
}

export default HomePage;
