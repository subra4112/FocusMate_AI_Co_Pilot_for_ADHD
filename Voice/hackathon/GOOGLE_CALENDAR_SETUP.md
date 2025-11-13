# Google Calendar Integration Setup

This guide will help you set up Google Calendar sync for your Voice Journal app.

## Quick Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Name it something like "Voice Journal"

### 2. Enable Google Calendar API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click on it and press **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (unless you have a workspace)
   - App name: **Voice Journal**
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue through the scopes (no need to add any)
   - Add yourself as a test user
4. Back to creating OAuth client ID:
   - Application type: **Desktop app**
   - Name: **Voice Journal Desktop**
   - Click **Create**

### 4. Download Credentials

1. After creating, you'll see a dialog with your Client ID and Secret
2. Click **DOWNLOAD JSON**
3. Save this file as `credentials.json` in your `hackathon/hackathon/` directory
   - **Location:** Same folder as `test_voice.py`

### 5. First Run Authentication

1. Run your app: `python test_voice.py`
2. A browser window will open asking you to sign in to Google
3. Sign in and grant permissions
4. The app will save a `token.json` file for future use
5. You're all set! 🎉

## File Structure

After setup, you should have:
```
hackathon/
├── hackathon/
│   ├── test_voice.py
│   ├── credentials.json    ← Your OAuth credentials (keep private!)
│   ├── token.json          ← Auto-generated after first auth
│   └── tasks/              ← Task JSON files
```

## Troubleshooting

### "credentials.json not found"
- Make sure the file is in `hackathon/hackathon/` directory
- Check the filename is exactly `credentials.json` (no extra extensions)

### "Access blocked: This app's request is invalid"
- Make sure you added yourself as a test user in OAuth consent screen
- Check that Google Calendar API is enabled

### "Calendar sync disabled"
- The app will still work! Tasks save locally
- Calendar sync is optional and fails gracefully
- Check console output for specific error messages

## Using Your Existing Client ID & Secret

If you already have a Client ID and Client Secret:

1. Copy `credentials.json.template` to `credentials.json`
2. Replace `YOUR_CLIENT_ID` with your actual client ID
3. Replace `YOUR_CLIENT_SECRET` with your actual client secret
4. Run the app and authenticate

## How It Works

- 🎤 You speak a task
- 📝 App transcribes and saves it
- 🔄 Background thread syncs to Google Calendar
- ✅ Calendar event created with priority color-coding
- 📅 Check your Google Calendar to see the event!

## Privacy & Security

- Your credentials stay on your machine
- `credentials.json` and `token.json` should NEVER be committed to git
- Add them to `.gitignore` to keep them private
- The app only requests Calendar access, nothing else

## Features

✅ Automatic real-time sync  
✅ Priority color coding (Red=high, Yellow=medium, Green=low)  
✅ 10-minute popup reminders  
✅ Supports timed events and all-day tasks  
✅ Includes your voice transcript in event description  
✅ Background threading (won't freeze UI)  
✅ Graceful fallback if sync fails  

Enjoy your integrated Voice Journal! 🎤📅

