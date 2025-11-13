# FocusMate - Your AI Co-Pilot for Executive Function

**Helping neurodivergent young adults master the executive function skills essential for post-college success.**

## 💙 Our Mission

FocusMate was created to support young adults navigating autism, dyslexia, ADHD, and mental health challenges as they transition into post-college life. We understand that executive function skills, like planning, organizing, prioritizing, and managing time, don't come naturally to everyone, and that's okay. FocusMate is here to bridge that gap.

### The Challenge We're Addressing

For many neurodivergent individuals, everyday tasks that seem simple to others can feel overwhelming:
- **Email overwhelm**: Inboxes become a source of anxiety, with important messages getting lost
- **Time blindness**: Difficulty estimating how long tasks will take or managing a schedule
- **Task initiation**: Knowing what to do but struggling to start
- **Working memory**: Keeping track of multiple responsibilities and deadlines
- **Emotional regulation**: Managing stress and anxiety while trying to stay organized

FocusMate doesn't try to "fix" these challenges, instead, it works with your unique brain to make daily life more manageable and less stressful.

## 🌟 How FocusMate Helps

### 📧 Email That Doesn't Overwhelm
Instead of drowning in an inbox, FocusMate helps you:
- **Automatically sorts** emails by what needs action vs. what's just information
- **Summarizes** long emails so you can quickly understand what matters
- **Extracts action items** so you don't have to hunt for what you need to do
- **Answers questions** about your inbox in plain language ("What emails need my response this week?")

### 📅 Planning That Actually Works
FocusMate creates realistic daily plans that:
- **Respects your energy levels** by scheduling breaks every 90 minutes
- **Estimates time realistically** so you're not constantly running behind
- **Blocks time visually** so you can see your day at a glance
- **Syncs with your calendar** so everything is in one place

### 🎤 Voice Input for When Writing Feels Hard
Sometimes the hardest part is getting thoughts out of your head. FocusMate lets you:
- **Speak your tasks** instead of typing them
- **Capture ideas quickly** before you forget them
- **Understand your emotions** to help you plan around your mental state

### 📱 Mobile Access When You Need It
Life doesn't happen at a desk. FocusMate goes with you:
- **Quick email triage** on your phone
- **See what's urgent** at a glance
- **ADHD-friendly design** that reduces visual clutter

## 🎯 Who This Is For

FocusMate is designed for:
- **Young adults** transitioning from college to career
- **Neurodivergent individuals** with ADHD, autism, dyslexia, or mental health challenges
- **Anyone** who struggles with executive function skills
- **People** who want to reduce daily stress and anxiety around organization

## 🚀 Getting Started

### What You'll Need

- A Google account (for email and calendar)
- An OpenAI API key (for AI features)
- Basic comfort with technology (we've tried to make it as simple as possible!)

### Quick Setup

1. **Set up your email connection** - Connect your Gmail so FocusMate can help organize it
2. **Connect your calendar** - Link Google Calendar to see everything in one place
3. **Start using it** - Begin with email triage or daily planning

See the [Technical Setup Guide](#technical-setup) below for detailed instructions.

## 💡 Real-World Impact

FocusMate helps with the executive function skills that matter most for post-college success:

### Task Management
- **Prioritization**: Automatically identifies what's urgent vs. what can wait
- **Organization**: Keeps all your tasks in one visual place
- **Completion tracking**: See what you've accomplished to build momentum

### Time Management
- **Realistic scheduling**: AI helps estimate how long things actually take
- **Time blocking**: Visual representation of your day reduces time blindness
- **Break reminders**: Prevents burnout with scheduled rest periods

### Information Management
- **Email organization**: No more lost important messages
- **Natural language search**: Find things by asking, not by remembering keywords
- **Summarization**: Get the gist without reading everything

### Emotional Regulation
- **Reduced overwhelm**: Breaking big tasks into manageable pieces
- **Anxiety reduction**: Knowing what needs attention reduces uncertainty
- **Accommodation**: Works with your brain, not against it

## 🎨 Design Philosophy

Every feature in FocusMate is designed with neurodivergence in mind:

- **Visual clarity**: Clean interfaces that don't overwhelm
- **Flexibility**: Multiple ways to interact (voice, text, visual)
- **Forgiveness**: Easy to fix mistakes and adjust plans
- **Transparency**: You always know what the AI is doing and why
- **Respect**: Never tries to "fix" you, just makes life easier

## 📚 Understanding Executive Function

Executive function skills are the mental processes that help us:
- Plan and organize
- Manage time effectively
- Remember important information
- Control impulses and emotions
- Solve problems flexibly

These skills are often challenging for neurodivergent individuals, but that doesn't mean they can't be supported. FocusMate acts as an external executive function system, a co-pilot that helps you navigate daily life with less stress and more success.

## 🤝 How to Contribute

We welcome contributions from:
- **Developers** who want to improve the technology
- **Users** who have ideas for features
- **Advocates** who want to spread the word
- **Anyone** who believes in supporting neurodivergent individuals

See the [Development Guide](#development) below for technical details.

## 💬 Support & Community

If you're using FocusMate and need help, or if you have ideas for how it could better serve the neurodivergent community, we want to hear from you. This project exists to help real people with real challenges.

---

## Technical Setup

*The following sections contain technical details for developers and users who want to set up FocusMate locally.*

### Prerequisites

- **Python 3.12+** (for backend services)
- **Node.js 18+** (for frontend applications)
- **Google Cloud Project** with Gmail and Calendar APIs enabled
- **OpenAI API Key** (for AI-powered features)
- **Google OAuth Credentials** (`credentials.json`)

### Installation

#### 1. Email Backend Setup

```bash
cd Email

# Create virtual environment
python -m venv my_env

# Activate virtual environment
# On Windows (PowerShell):
.\my_env\Scripts\Activate.ps1
# On macOS/Linux:
source my_env/bin/activate

# Install dependencies
pip install -r req.txt

# Set up environment variables
cp env.sample .env
# Edit .env and add your OPENAI_API_KEY

# Set up Google OAuth
python google_oauth_setup.py
python google_oauth_calendar_setup.py
```

#### 2. Calendar Web App Setup

```bash
cd Calendar/focusmate-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The calendar app will be available at `http://localhost:5173`

#### 3. Voice Service Setup

```bash
cd Voice/hackathon

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env)
# Add OPENAI_API_KEY and ELEVENLABS_API_KEY if needed

# Start voice server
uvicorn enhanced_server:app --reload --port 8001
```

#### 4. Mobile App Setup (Optional)

```bash
cd Frontend/FocusMateMailApp

# Install dependencies
npm install

# Create .env file
echo "EXPO_PUBLIC_API_URL=http://127.0.0.1:8000" > .env
echo "EXPO_PUBLIC_VOICE_API_URL=http://127.0.0.1:8001" >> .env

# Start Expo
npm start
```

### Running the Full Stack

#### Option 1: PowerShell Script (Windows)

```powershell
.\start_focusmate.ps1 -ApiHost http://127.0.0.1:8000 -VoiceApiHost http://127.0.0.1:8001
```

#### Option 2: Manual Start

**Terminal 1 - Email Backend:**
```bash
cd Email
.\my_env\Scripts\Activate.ps1  # or source my_env/bin/activate on macOS/Linux
uvicorn api.server:app --reload --port 8000
```

**Terminal 2 - Calendar App:**
```bash
cd Calendar/focusmate-app
npm run dev
```

**Terminal 3 - Voice Service:**
```bash
cd Voice/hackathon
uvicorn enhanced_server:app --reload --port 8001
```

**Terminal 4 - Mobile App (Optional):**
```bash
cd Frontend/FocusMateMailApp
npm start
```

## 📁 Project Structure

```
FocusMate_AI_Co_Pilot_for_ADHD/
├── Email/              # Email processing and organization
├── Calendar/           # Calendar and task management web app
├── Voice/              # Voice input and transcription
├── Frontend/           # Mobile app for on-the-go access
└── Plan/               # AI-powered daily planning
```

### Module Details

- **Email Module**: Processes and organizes emails, extracts tasks, creates calendar events
- **Calendar Module**: Visual calendar interface, task management, day planning
- **Voice Module**: Speech-to-text, task extraction from voice, emotion detection
- **Frontend Module**: Mobile interface for email triage and task management
- **Plan Module**: Automated daily scheduling with time blocking and breaks

## 🔑 Environment Variables

### Email Backend (`.env` in `/Email`)
```env
OPENAI_API_KEY=sk-...
SUPERMEMORY_API_KEY=optional
```

### Voice Service (`.env` in `/Voice/hackathon`)
```env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=optional
```

### Mobile App (`.env` in `/Frontend/FocusMateMailApp`)
```env
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
EXPO_PUBLIC_VOICE_API_URL=http://127.0.0.1:8001
```

## 🔧 API Endpoints

### Email Backend (Port 8000)
- `GET /health` - Health check
- `GET /emails?limit=N` - Fetch cached email summaries
- `POST /emails/refresh` - Ingest new Gmail data
- `POST /emails/search` - Natural language inbox search

### Voice Service (Port 8001)
- `POST /stt` - Speech-to-text transcription (file upload)
- `POST /stt/mic` - Server-side microphone recording

## 📚 Documentation

Each module has its own detailed README:
- [Email Module README](Email/README.md)
- [Calendar Module README](Calendar/focusmate-app/README.md)
- [Mobile App README](Frontend/FocusMateMailApp/README.md)

Additional documentation:
- [Google Calendar Setup Guide](Calendar/focusmate-app/GOOGLE_CALENDAR_SETUP.md)
- [Focus Rules](Plan/FOCUS_RULES.md)

## 🐛 Troubleshooting

### Common Issues

**OAuth Authentication Errors**
- Delete `token.json` and re-run OAuth setup scripts
- Ensure Google Cloud project has correct scopes enabled

**Port Already in Use**
- Change port numbers in configuration files
- Kill processes using the ports: `lsof -ti:8000 | xargs kill` (macOS/Linux)

**Module Not Found Errors**
- Ensure virtual environments are activated
- Reinstall dependencies: `pip install -r req.txt` or `npm install`

**API Connection Errors**
- Verify backend services are running
- Check environment variables are set correctly
- Ensure CORS is configured properly

## 🛠️ Development

### Adding New Features

1. **Email Processing**: Modify `Email/services/email_processor.py`
2. **Calendar Integration**: Update `Calendar/focusmate-app/src/components/`
3. **Voice Features**: Extend `Voice/hackathon/voice/` module
4. **Mobile UI**: Edit `Frontend/FocusMateMailApp/src/screens/`

### Testing

- **Email Backend**: Use `focusmate_app.py --unread 7` for CLI testing
- **API**: Test endpoints with `curl` or Postman
- **Frontend**: Use browser dev tools and React DevTools
- **Mobile**: Use Expo Go app for live preview

## 📝 License

MIT License - See individual module READMEs for specific licensing information.

---

## 👥 Team

**Made with ❤️ by Team Neuro X**

FocusMate was created by a dedicated team passionate about supporting neurodivergent individuals:

1. **Aneesh Jayan Prabhu**
2. **Samyogita Bhandari**
3. **Sehastrajit Selvachandran**
4. **Subramanian Raj Narayanan**
5. **Vibha Swaminathan**

---

**Made with ❤️ to help neurodivergent young adults thrive in post-college life.**

*FocusMate is designed to support, not replace, professional mental health care. If you're struggling with executive function challenges, consider working with a therapist or coach who specializes in neurodivergence.*
