import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Mic, Calendar, CheckSquare, Sparkles } from 'lucide-react';
import './BottomNav.css';

function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Mic, label: 'Voice' },
    { path: '/calendar', icon: Calendar, label: 'Schedule' },
    { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
    { path: '/plan', icon: Sparkles, label: 'Plan Day' }
  ];

  return (
    <nav className="bottom-nav">
      {navItems.map(({ path, icon: Icon, label }) => (
        <button
          key={path}
          onClick={() => navigate(path)}
          className={`nav-item ${location.pathname === path ? 'active' : ''}`}
        >
          <Icon size={24} />
          <span>{label}</span>
        </button>
      ))}
    </nav>
  );
}

export default BottomNav;
