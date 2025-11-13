# 🚀 QUICK START GUIDE - First React Project

## Step-by-Step Instructions for Complete Beginners

### 1. Install Node.js (if you haven't)

**Windows/Mac:**
1. Go to https://nodejs.org/
2. Click the big green button "Download Node.js (LTS)"
3. Run the installer
4. Click "Next" through everything (keep defaults)
5. Restart your computer

**Check it worked:**
Open Terminal (Mac) or Command Prompt (Windows) and type:
```bash
node --version
```
You should see something like `v18.17.0`

### 2. Get Your Project Files

You should have a folder called `focusmate-app` with all the files.

### 3. Open Terminal/Command Prompt

**Mac:**
- Press `Cmd + Space`
- Type "Terminal"
- Press Enter

**Windows:**
- Press `Windows Key`
- Type "cmd"
- Press Enter

### 4. Navigate to Your Project

```bash
cd path/to/focusmate-app
```

Replace `path/to/focusmate-app` with where you saved it. 

**Example (Mac):**
```bash
cd ~/Downloads/focusmate-app
```

**Example (Windows):**
```bash
cd C:\Users\YourName\Downloads\focusmate-app
```

### 5. Install Dependencies

Type this command and press Enter:
```bash
npm install
```

Wait 2-3 minutes. You'll see lots of text scrolling. That's normal!

### 6. Start the App

Type this command and press Enter:
```bash
npm run dev
```

You should see:
```
  VITE v5.0.7  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 7. Open in Browser

The app should open automatically! If not:
- Open your browser
- Go to: http://localhost:3000

### 🎉 You're Done!

Your FocusMate app is now running!

## What You'll See

1. **Voice Tab** - Big microphone button (home screen)
2. **Schedule Tab** - Calendar view of tasks
3. **Tasks Tab** - List of all your tasks
4. **Plan Day Tab** - AI schedules your day

## Try These Things

1. Click the **"Add Sample Task"** button to add a task
2. Go to **Tasks tab** - click checkboxes to complete tasks
3. Go to **Plan Day tab** - click "Generate Schedule" to see AI magic
4. Go to **Schedule tab** - see your tasks on a calendar

## Common Issues & Fixes

### "npm is not recognized"
→ You need to install Node.js (see Step 1)

### "Port 3000 already in use"
→ That's okay! It will use port 3001. Just open http://localhost:3001

### "Cannot find module"
→ Make sure you ran `npm install` first

### Screen is blank
→ Press F12 in browser, look at Console tab for errors

## Stopping the App

In the Terminal/Command Prompt, press:
- **Mac/Linux:** `Ctrl + C`
- **Windows:** `Ctrl + C`

## Starting Again

Just run:
```bash
npm run dev
```

## Folder Structure (Don't Delete These!)

```
focusmate-app/
├── node_modules/     ← Auto-created by npm install
├── src/              ← Your code files
├── index.html
├── package.json
└── vite.config.js
```

## Need Help?

1. Make sure Node.js is installed: `node --version`
2. Make sure you're in the right folder: `pwd` (Mac) or `cd` (Windows)
3. Try deleting `node_modules` and running `npm install` again
4. Check browser console (F12) for errors

## What's Next?

1. **Play with the app** - Click everything!
2. **Customize colors** - Edit the CSS files
3. **Add real voice input** - Connect to backend API
4. **Deploy online** - Use services like Vercel or Netlify

---

## Commands Cheat Sheet

```bash
npm install          # Install dependencies (do once)
npm run dev         # Start development server
npm run build       # Build for production
Ctrl + C            # Stop the server
```

---

🎊 Congratulations on your first React app!
