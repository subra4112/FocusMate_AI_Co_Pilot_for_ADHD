# FocusMate - AI Copilot for ADHD and Anxiety

Your personal AI assistant that helps manage tasks, emotions, and daily planning.

## 🚀 Getting Started (First React Project!)

### Prerequisites

You need to have **Node.js** installed on your computer. 

1. **Check if you have Node.js:**
   ```bash
   node --version
   ```
   
   If you see a version number (like v18.x.x), you're good to go!
   
2. **If you don't have Node.js:**
   - Go to https://nodejs.org/
   - Download the LTS version (recommended)
   - Install it following the instructions

### Installation Steps

1. **Navigate to the project folder:**
   ```bash
   cd focusmate-app
   ```

2. **Install all dependencies:**
   ```bash
   npm install
   ```
   
   This will download all the packages the app needs. It might take 2-3 minutes.

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The app will automatically open in your browser at `http://localhost:3000`

### That's it! 🎉

Your app should now be running. You'll see:
- **Voice tab**: Home screen with mic button
- **Schedule tab**: Calendar view of your tasks
- **Tasks tab**: List of all tasks
- **Plan Day tab**: AI-powered daily scheduler

## 📱 Features

### ✅ Current Features
- **Task Management**: View, create, and complete tasks
- **Calendar View**: See tasks on a visual calendar
- **Priority System**: High, medium, low priority tasks
- **Plan My Day**: AI automatically schedules your tasks with breaks
- **Time Blocking**: Estimate task duration and see time blocks
- **Task Filtering**: View all, active, or completed tasks
- **Sample Data**: Pre-loaded with your JSON tasks

### 🔮 Ready for Backend Integration
- Voice input (ready for speech-to-text API)
- Task extraction from voice
- Google Calendar sync
- Email integration
- Emotion detection

## 📁 Project Structure

```
focusmate-app/
├── src/
│   ├── components/          # Reusable components
│   │   ├── BottomNav.jsx    # Navigation bar
│   │   ├── TaskCalendar.jsx # Calendar component
│   │   ├── TaskList.jsx     # Task list view
│   │   └── DayPlanner.jsx   # Day planning AI
│   │
│   ├── pages/               # Main screens
│   │   ├── HomePage.jsx     # Voice input screen
│   │   ├── CalendarPage.jsx # Calendar view
│   │   ├── TasksPage.jsx    # Tasks list
│   │   └── PlanMyDayPage.jsx # Day planner
│   │
│   ├── App.jsx              # Main app component
│   ├── App.css              # Global styles
│   └── main.jsx             # Entry point
│
├── index.html               # HTML template
├── package.json             # Dependencies
└── vite.config.js           # Build config
```

## 🎨 Your JSON Task Format

The app uses this JSON structure for tasks:

```json
{
  "id": "unique-id",
  "created_at": "2025-11-09T14:16:43.947332",
  "action": "Get groceries",
  "due_date": "2025-11-09",
  "due_time": "15:00",
  "due_datetime": "2025-11-09T15:00:00",
  "estimated_minutes": 30,
  "calendar_event_id": null,
  "scheduled_start": null,
  "scheduled_end": null,
  "priority": "high",
  "confidence": 0.9,
  "rationale": "Extracted from multi-task analysis",
  "transcript": "Voice input text...",
  "completed": false,
  "status": "todo"
}
```

## 🔧 Common Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐛 Troubleshooting

### Port already in use?
If port 3000 is busy, the app will automatically try port 3001, 3002, etc.

### npm install fails?
Try:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Page is blank?
Check the browser console (F12) for errors.

### Module not found errors?
Make sure all files are in the correct folders as shown in the structure above.

## 📝 Adding Your Backend

When you're ready to connect to your Python backend:

1. Update the API calls in components to point to your backend URL
2. Add axios calls like:
   ```javascript
   import axios from 'axios';
   
   const response = await axios.post('http://localhost:8000/api/tasks', taskData);
   ```

## 🎓 Learning Resources

Since this is your first React project:

- **React Docs**: https://react.dev/learn
- **Vite Guide**: https://vitejs.dev/guide/
- **React Router**: https://reactrouter.com/
- **Lucide Icons**: https://lucide.dev/

## 🌟 Next Steps

1. **Test the app** - Click around and see how it works
2. **Modify colors** - Change the CSS files to match your brand
3. **Add more tasks** - Use the "Add Sample Task" button
4. **Plan your day** - Try the "Plan My Day" feature
5. **Connect your backend** - When ready, integrate with FastAPI

## 💡 Tips

- Tasks are saved in browser localStorage (they persist on refresh!)
- The calendar uses color coding: Red = High, Yellow = Medium, Green = Low
- The day planner automatically adds breaks every 90 minutes
- Click on any task in the calendar to see details

## 🤝 Need Help?

- Check the browser console (F12) for error messages
- Make sure all dependencies installed correctly
- Try restarting the dev server (`npm run dev`)

---

Made with ❤️ for helping people with ADHD stay focused and calm.
