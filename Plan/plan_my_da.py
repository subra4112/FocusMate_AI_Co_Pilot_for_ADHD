from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import os.path
import pickle
import os
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TIMELINE_PATH = os.path.join(BASE_DIR, 'day_timeline.json')

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# Use system local timezone instead of hardcoded timezone
MY_TIMEZONE = datetime.datetime.now().astimezone().tzinfo

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_calendar_service():
    """Authenticate and return the Google Calendar service."""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_todays_events():
    """Fetch all events for today from Google Calendar."""
    service = get_calendar_service()
    
    # Use system local time
    now = datetime.datetime.now().astimezone()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + datetime.timedelta(days=1)
    
    time_min = today.astimezone(ZoneInfo('UTC')).isoformat()
    time_max = tomorrow.astimezone(ZoneInfo('UTC')).isoformat()
    
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        all_events = []
        
        for calendar in calendars:
            cal_id = calendar['id']
            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            all_events.extend(events)
        
        all_events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
        
        return all_events, now
        
    except Exception as e:
        print(f"Error fetching events: {e}")
        return [], now

def parse_event_details(event):
    """Extract detailed information from an event."""
    details = {
        'summary': event.get('summary', 'Untitled'),
        'location': event.get('location', ''),
        'description': event.get('description', ''),
        'event_id': event.get('id', ''),
    }
    
    if 'dateTime' in event['start']:
        # Convert to system local timezone
        start_time = datetime.datetime.fromisoformat(
            event['start']['dateTime'].replace('Z', '+00:00')
        ).astimezone()
        end_time = datetime.datetime.fromisoformat(
            event['end']['dateTime'].replace('Z', '+00:00')
        ).astimezone()
        
        details['start'] = start_time
        details['end'] = end_time
        details['duration_minutes'] = int((end_time - start_time).total_seconds() / 60)
        details['is_all_day'] = False
    else:
        details['start'] = event['start'].get('date')
        details['end'] = event['end'].get('date')
        details['is_all_day'] = True
        details['duration_minutes'] = 0
    
    return details

def load_existing_timeline():
    """Load existing timeline if it exists."""
    if os.path.exists(TIMELINE_PATH):
        try:
            with open(TIMELINE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing timeline: {e}")
    return None

def generate_focus_prep_routine(next_event_time, next_event_details, current_time, is_first_task=False, time_since_last_task=None):
    """Generate a focus preparation routine based on available time and time of day.
    Only generates for:
    1. First task of the day
    2. When there's a 4+ hour gap since last task
    Ensures routine finishes BEFORE task starts and is max 5 minutes."""
    
    time_until_event = int((next_event_time - current_time).total_seconds() / 60)
    
    # Check if we should generate focus routine at all
    if not is_first_task and time_since_last_task is not None:
        hours_since_last = time_since_last_task / 60  # Convert minutes to hours
        if hours_since_last < 4:
            print(f"ℹ️  Only {hours_since_last:.1f} hours since last task - skipping focus routine (continuous work)")
            return None
        else:
            print(f"✓ {hours_since_last:.1f} hours since last task - adding focus routine (long break)")
    
    # If task is too soon (less than 6 minutes), skip focus routine
    if time_until_event < 6:
        print(f"⚠️  Task starts in {time_until_event} min - too soon for focus routine")
        return None
    
    # Cap the routine duration at 5 minutes max
    # Leave at least 1 minute buffer before task starts
    max_routine_duration = min(time_until_event - 1, 5)
    
    if max_routine_duration < 3:
        print(f"⚠️  Only {time_until_event} min until task - skipping focus routine")
        return None
    
    current_hour = current_time.hour
    
    # Determine time of day context
    if current_hour < 6:
        time_context = "very early morning (pre-dawn)"
    elif current_hour < 9:
        time_context = "early morning"
    elif current_hour < 12:
        time_context = "late morning"
    elif current_hour < 14:
        time_context = "early afternoon (post-lunch)"
    elif current_hour < 17:
        time_context = "mid-afternoon"
    elif current_hour < 20:
        time_context = "evening"
    else:
        time_context = "late evening/night"
    
    # Keep focus routine simple and short
    if is_first_task:
        focus_areas = """Quick morning startup:
1. Quick physical prep (30 sec - sit properly, adjust desk/monitor)
2. Mental reset (1-2 min - 3 deep breaths, clear mind)
3. Workspace ready (1-2 min - open apps, get water/coffee, headphones on)"""
    else:
        focus_areas = """Quick refocus after long break:
1. Mental reset (1 min - breathe, let go of break activities)
2. Physical refresh (1-2 min - quick stretch, adjust posture)
3. Get ready (1-2 min - open task materials, set playlist)"""
    
    prompt = f"""You are a productivity coach. Create a VERY SHORT and PRACTICAL focus routine.

Current time: {current_time.strftime('%I:%M %p')} ({time_context})
Next task: {next_event_details['summary']} at {next_event_time.strftime('%I:%M %p')}
Available time: {time_until_event} minutes
Maximum routine duration: {max_routine_duration} minutes (MUST NOT EXCEED - KEEP IT SHORT!)
Context: {"First task of the day" if is_first_task else "Long break (4+ hours) - need to refocus"}

CRITICAL CONSTRAINTS:
- Total routine MUST be {max_routine_duration} minutes or LESS
- Keep it SIMPLE and FAST - this is just a quick prep
- Routine MUST finish by {(next_event_time - datetime.timedelta(minutes=1)).strftime('%I:%M %p')}
- Start time should be {current_time.strftime('%I:%M %p')} or shortly after

{focus_areas}

Return a JSON array with 2-3 QUICK steps (total ≤ {max_routine_duration} min):
[
  {{
    "time": "HH:MM AM/PM",
    "duration_minutes": 2,
    "activity": "Activity name",
    "description": "Brief, specific actions",
    "purpose": "Quick reason"
  }}
]

IMPORTANT: 
- Keep descriptions SHORT and ACTIONABLE
- First step starts at or just after current time
- Sum of all duration_minutes must be ≤ {max_routine_duration}
- Times must be sequential and not overlap with task
- Return ONLY valid JSON"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a productivity expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        
        routine = json.loads(content)
        
        # Validate that routine doesn't overlap with task
        total_duration = sum(step['duration_minutes'] for step in routine)
        if total_duration > max_routine_duration:
            print(f"⚠️  Generated routine ({total_duration} min) exceeds limit ({max_routine_duration} min), truncating...")
            # Truncate steps to fit
            adjusted_routine = []
            running_total = 0
            for step in routine:
                if running_total + step['duration_minutes'] <= max_routine_duration:
                    adjusted_routine.append(step)
                    running_total += step['duration_minutes']
            routine = adjusted_routine
        
        print(f"✓ Focus routine: {sum(step['duration_minutes'] for step in routine)} min, finishes at {(current_time + datetime.timedelta(minutes=sum(step['duration_minutes'] for step in routine))).strftime('%I:%M %p')}")
        
        return routine
    
    except Exception as e:
        print(f"Error generating focus routine: {e}")
        return None

def create_optimized_schedule_with_breaks(events, current_time):
    """Use LLM to create an optimized schedule with appropriate breaks for ALL events."""
    
    parsed_events = []
    for event in events:
        details = parse_event_details(event)
        if not details['is_all_day']:
            # Include ALL events, past and future
            parsed_events.append(details)
    
    if not parsed_events:
        return None
    
    schedule_info = []
    for event in parsed_events:
        # Mark if event is in past or future
        is_past = event['start'] < current_time
        schedule_info.append({
            'title': event['summary'],
            'start': event['start'].strftime('%I:%M %p'),
            'end': event['end'].strftime('%I:%M %p'),
            'duration': event['duration_minutes'],
            'description': event['description'][:200] if event['description'] else '',
            'location': event['location'],
            'event_id': event['event_id'],
            'is_past': is_past
        })
    
    prompt = f"""Analyze ALL tasks for today and insert appropriate breaks WITHIN each long task.

Current time: {current_time.strftime('%I:%M %p')}

ALL Tasks Today (past and future):
{json.dumps(schedule_info, indent=2)}

Rules:
- Process ALL tasks regardless of is_past flag
- For past tasks: Show them as-is with their original structure
- For future tasks: Insert breaks where needed
- 90+ minutes: Break every 60-90 min (10-15 min)
- 60-90 minutes: One mid-task break (5-10 min)
- Under 60 minutes: No break needed
- Match break type to work type
- Keep original start/end times
- Include event_id in response

Return JSON array with ALL tasks:
[
  {{
    "event_id": "original_event_id",
    "original_task": "task name",
    "start": "HH:MM AM/PM",
    "end": "HH:MM AM/PM",
    "is_past": true/false,
    "segments": [
      {{"type": "work", "start": "HH:MM AM/PM", "end": "HH:MM AM/PM", "activity": "task"}},
      {{"type": "break", "start": "HH:MM AM/PM", "end": "HH:MM AM/PM", "duration_minutes": 10, "activity": "break activity", "reason": "why needed"}}
    ]
  }}
]

IMPORTANT: Include EVERY task from the input, marking past ones with is_past: true. Return ONLY valid JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a productivity expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        
        schedule = json.loads(content)
        return schedule
    
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return None

def merge_timelines(existing_timeline, new_schedule, focus_routine, current_time, focus_metadata=None):
    """Merge new schedule with existing timeline - preserve past, update future."""
    
    # For fresh timeline or major updates, just create new
    # The new_schedule now contains ALL tasks (past and future) from LLM
    return create_timeline_json(focus_routine, new_schedule, current_time, focus_metadata)

def create_timeline_json(focus_routine, optimized_schedule, current_time, focus_metadata=None):
    """Create a unified timeline JSON structure."""
    
    # Get system timezone name
    import time
    timezone_name = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    
    timeline = {
        "generated_at": current_time.isoformat(),
        "last_updated": current_time.isoformat(),
        "timezone": timezone_name,
        "focus_routine_info": {
            "included": focus_routine is not None,
            "reason": focus_metadata if focus_metadata else "No focus routine needed",
            "max_duration_minutes": 5 if focus_routine else 0
        },
        "sections": []
    }
    
    # Add focus routine
    if focus_routine:
        focus_section = {
            "section_type": "focus_routine",
            "title": "Focus Preparation Routine",
            "max_duration": "5 minutes",
            "items": []
        }
        
        for step in focus_routine:
            focus_section["items"].append({
                "type": "routine",
                "time": step["time"],
                "duration_minutes": step["duration_minutes"],
                "activity": step["activity"],
                "description": step["description"],
                "purpose": step["purpose"]
            })
        
        timeline["sections"].append(focus_section)
    
    # Add work schedule
    if optimized_schedule:
        work_section = {
            "section_type": "work_schedule",
            "title": "Work Schedule with Breaks",
            "items": []
        }
        
        for task_block in optimized_schedule:
            task_item = {
                "type": "task_block",
                "event_id": task_block.get("event_id", ""),
                "original_task": task_block["original_task"],
                "start": task_block["start"],
                "end": task_block["end"],
                "is_past": task_block.get("is_past", False),
                "segments": task_block["segments"]
            }
            
            work_section["items"].append(task_item)
        
        timeline["sections"].append(work_section)
    
    return timeline

def create_timeline_json_with_multiple_focus(all_focus_routines, optimized_schedule, current_time):
    """Create a unified timeline JSON structure with multiple focus routines."""
    
    # Build summary for focus routine info
    if all_focus_routines:
        reasons = [fr['reason'] for fr in all_focus_routines]
        focus_metadata = f"{len(all_focus_routines)} focus routine(s): " + "; ".join(reasons)
    else:
        focus_metadata = "No focus routines needed"
    
    # Get system timezone name
    import time
    timezone_name = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    
    timeline = {
        "generated_at": current_time.isoformat(),
        "last_updated": current_time.isoformat(),
        "timezone": timezone_name,
        "focus_routine_info": {
            "included": len(all_focus_routines) > 0,
            "reason": focus_metadata,
            "max_duration_minutes": 5,
            "count": len(all_focus_routines)
        },
        "sections": []
    }
    
    # Add all focus routines as separate sections
    for i, focus_info in enumerate(all_focus_routines):
        focus_section = {
            "section_type": "focus_routine",
            "title": f"Focus Routine #{i+1}: Before {focus_info['task_name']}",
            "max_duration": "5 minutes",
            "for_task": focus_info['task_name'],
            "task_start_time": focus_info['task_start'].strftime('%I:%M %p'),
            "reason": focus_info['reason'],
            "items": []
        }
        
        for step in focus_info['routine']:
            focus_section["items"].append({
                "type": "routine",
                "time": step["time"],
                "duration_minutes": step["duration_minutes"],
                "activity": step["activity"],
                "description": step["description"],
                "purpose": step["purpose"]
            })
        
        timeline["sections"].append(focus_section)
    
    # Add work schedule
    if optimized_schedule:
        work_section = {
            "section_type": "work_schedule",
            "title": "Work Schedule with Breaks",
            "items": []
        }
        
        for task_block in optimized_schedule:
            task_item = {
                "type": "task_block",
                "event_id": task_block.get("event_id", ""),
                "original_task": task_block["original_task"],
                "start": task_block["start"],
                "end": task_block["end"],
                "is_past": task_block.get("is_past", False),
                "segments": task_block["segments"]
            }
            
            work_section["items"].append(task_item)
        
        timeline["sections"].append(work_section)
    
    return timeline

def save_timeline_json(timeline, filename="day_timeline.json"):
    """Save timeline to JSON file."""
    filepath = os.path.join(BASE_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    
    return filepath

def display_complete_schedule(timeline, current_time):
    """Display the complete timeline."""
    
    print("\n" + "=" * 80)
    print("YOUR COMPLETE DAY PLAN")
    print(f"Generated at: {current_time.strftime('%I:%M %p %Z')}")
    print("=" * 80)
    
    # Separate focus routines from work schedule
    focus_sections = []
    work_sections = []
    
    for section in timeline.get('sections', []):
        if section['section_type'] == 'focus_routine':
            focus_sections.append(section)
        else:
            work_sections.append(section)
    
    # Display all focus routines first
    if focus_sections:
        print(f"\n{'='*80}")
        print(f"FOCUS PREPARATION ROUTINES ({len(focus_sections)} total)")
        print(f"{'='*80}")
        
        for section in focus_sections:
            print(f"\n{'-'*80}")
            print(f"{section['title']}")
            if 'task_start_time' in section:
                print(f"For task at: {section['task_start_time']}")
            if 'reason' in section:
                print(f"Reason: {section['reason']}")
            print(f"{'-'*80}")
            
            for item in section['items']:
                print(f"\n  {item['time']} ({item['duration_minutes']} min)")
                print(f"  {item['activity']}")
                print(f"    Actions: {item['description']}")
                print(f"    Purpose: {item['purpose']}")
    
    # Display work schedule
    for section in work_sections:
        print(f"\n{'='*80}")
        print(f"{section['title']}")
        print(f"{'='*80}")
        
        for item in section['items']:
            status = " [COMPLETED]" if item.get('is_past', False) else ""
            print(f"\n{'-'*80}")
            print(f"{item['original_task']}{status}")
            print(f"{item['start']} - {item['end']}")
            print(f"{'-'*80}")
            
            for segment in item['segments']:
                if segment['type'] == 'work':
                    print(f"\n  WORK: {segment['start']} - {segment['end']}")
                    print(f"    {segment['activity']}")
                else:
                    print(f"\n  BREAK: {segment['start']} - {segment['end']} ({segment['duration_minutes']} min)")
                    print(f"    Activity: {segment['activity']}")
                    print(f"    Reason: {segment['reason']}")
    
    print("\n" + "=" * 80)
    print("PRODUCTIVITY TIPS:")
    if focus_sections:
        print(f"  - {len(focus_sections)} focus routine(s) added before key tasks")
    print("  - Follow your focus routines to get into the zone")
    print("  - Respect your breaks - they enhance performance")
    print("  - Set alarms for transitions")
    print("  - Completed tasks are marked with [COMPLETED]")
    print("  - Re-run this script when new tasks are added")
    print("=" * 80)

def main():
    print("=" * 80)
    print("DYNAMIC DAY PLANNER - Smart Timeline Updates")
    print("=" * 80)
    
    events, current_time = get_todays_events()
    
    if not events:
        print("\nNo events scheduled for today.")
        return
    
    # Parse all events to find gaps
    parsed_events = []
    for event in events:
        details = parse_event_details(event)
        if not details['is_all_day']:
            parsed_events.append(details)
    
    if not parsed_events:
        print("\nNo time-based events today.")
        return
    
    # Load existing timeline
    existing_timeline = load_existing_timeline()
    
    if existing_timeline:
        print(f"\nFound existing timeline. Updating with latest schedule...")
        print(f"Last updated: {existing_timeline.get('last_updated', 'unknown')}")
    
    print(f"\nCurrent time: {current_time.strftime('%I:%M %p')}")
    
    # Analyze ALL tasks and determine which ones need focus routines
    print("\n" + "=" * 80)
    print("ANALYZING ALL TASKS FOR FOCUS ROUTINE NEEDS:")
    print("=" * 80)
    
    tasks_needing_focus = []
    
    for i, task in enumerate(parsed_events):
        # Skip past tasks
        if task['start'] < current_time:
            continue
        
        needs_focus = False
        reason = ""
        gap_hours = 0
        
        if i == 0:
            # First task of the day
            needs_focus = True
            reason = "First task of the day"
            print(f"\n✓ {task['summary']} at {task['start'].strftime('%I:%M %p')}")
            print(f"  → FIRST task - focus routine will be added")
        else:
            # Check gap from previous task
            prev_task = parsed_events[i - 1]
            gap_minutes = (task['start'] - prev_task['end']).total_seconds() / 60
            gap_hours = gap_minutes / 60
            
            if gap_hours >= 4.0:
                needs_focus = True
                reason = f"Long break ({gap_hours:.1f} hours gap between tasks)"
                print(f"\n✓ {task['summary']} at {task['start'].strftime('%I:%M %p')}")
                print(f"  → Gap: {gap_hours:.1f} hours (>= 4 hours) - focus routine will be added")
            else:
                print(f"\n✗ {task['summary']} at {task['start'].strftime('%I:%M %p')}")
                print(f"  → Gap: {gap_hours:.1f} hours (< 4 hours) - no focus routine")
        
        if needs_focus:
            # Check if we have enough time before task to add focus routine
            time_until_task = (task['start'] - current_time).total_seconds() / 60
            if time_until_task >= 6:  # Need at least 6 minutes
                tasks_needing_focus.append({
                    'task': task,
                    'reason': reason,
                    'is_first': (i == 0)
                })
            else:
                print(f"  ⚠️  But task starts in {time_until_task:.1f} min - too soon to add focus routine")
    
    print("=" * 80)
    print(f"\nTotal tasks needing focus routines: {len(tasks_needing_focus)}")
    
    # Generate focus routines for all tasks that need them
    all_focus_routines = []
    
    for task_info in tasks_needing_focus:
        task = task_info['task']
        print(f"\nGenerating focus routine for: {task['summary']}")
        
        # For the focus routine, use current time or a reasonable time before the task
        # If task is far in future, we'll generate it to start ~5-10 min before task
        time_until_task = (task['start'] - current_time).total_seconds() / 60
        
        if time_until_task > 30:
            # Task is far in future - schedule focus routine to start 10 min before
            routine_start_time = task['start'] - datetime.timedelta(minutes=10)
        else:
            # Task is soon - start focus routine now or shortly after current time
            routine_start_time = current_time
        
        focus_routine = generate_focus_prep_routine(
            task['start'],
            task,
            routine_start_time,
            is_first_task=task_info['is_first'],
            time_since_last_task=240 if not task_info['is_first'] else None  # Pass 240 to indicate it's valid
        )
        
        if focus_routine:
            all_focus_routines.append({
                'routine': focus_routine,
                'task_name': task['summary'],
                'task_start': task['start'],
                'reason': task_info['reason']
            })
    
    print(f"\nSuccessfully generated {len(all_focus_routines)} focus routine(s)")
    
    # Generate work schedule with breaks
    print("\nGenerating optimized schedule with breaks...\n")
    optimized_schedule = create_optimized_schedule_with_breaks(events, current_time)
    
    # Create timeline with ALL focus routines
    timeline = create_timeline_json_with_multiple_focus(
        all_focus_routines,
        optimized_schedule,
        current_time
    )
    
    # Save to JSON file
    filepath = save_timeline_json(timeline)
    
    # Display everything
    display_complete_schedule(timeline, current_time)
    
    print(f"\n\nTimeline saved to: {filepath}")
    print("\nYour complete day timeline includes:")
    print("  - All tasks from start of day to end")
    print("  - Past tasks marked as [COMPLETED]")
    print("  - Future tasks with break recommendations")
    if all_focus_routines:
        print(f"  - {len(all_focus_routines)} Focus routine(s) (5 min max each, for first task or 4+ hour gaps)")
    else:
        print("  - No focus routines (continuous work schedule)")
    print("\nWhen new tasks are added, re-run to update future schedule only!")

if __name__ == '__main__':
    main()