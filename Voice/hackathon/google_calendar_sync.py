# google_calendar_sync.py
import os
import json
import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarSync:
    def __init__(self, tasks_dir: str = "tasks", credentials_file: str = "credentials.json"):
        """
        Initialize Google Calendar sync.
        
        Args:
            tasks_dir: Directory containing task JSON files
            credentials_file: Path to OAuth2 credentials file from Google Cloud Console
        """
        self.tasks_dir = tasks_dir
        self.credentials_file = credentials_file
        self.service = None
        self.calendar_id = 'primary'  # Use primary calendar
        
    def authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # Try to load from environment variables first (if refresh token is provided)
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        
        if client_id and client_secret and refresh_token:
            # Create credentials from environment variables
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': SCOPES
            }
            
            # Save to token.json if it doesn't exist
            if not os.path.exists('token.json'):
                import json
                with open('token.json', 'w') as token_file:
                    json.dump(token_data, token_file, indent=2)
                print("[INFO] Created token.json from environment variables")
            
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
        # The file token.json stores the user's access and refresh tokens
        elif os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found.\n"
                        "Either:\n"
                        "1. Add to .env: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN\n"
                        "2. Or download credentials.json from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                # Use fixed port 8080 for web application OAuth
                creds = flow.run_local_server(port=8080)
                
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("[OK] Successfully authenticated with Google Calendar")
    
    def load_tasks(self):
        """Load all task JSON files from the tasks directory."""
        tasks = []
        tasks_path = Path(self.tasks_dir)
        
        if not tasks_path.exists():
            print(f"[WARNING] Tasks directory '{self.tasks_dir}' not found")
            return tasks
        
        for json_file in tasks_path.glob("task_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    task['_filename'] = json_file.name
                    tasks.append(task)
            except Exception as e:
                print(f"[WARNING] Error loading {json_file.name}: {e}")
        
        print(f"[OK] Loaded {len(tasks)} tasks from {self.tasks_dir}/")
        return tasks
    
    def parse_due_datetime(self, task):
        """
        Parse due date/time from task.
        Returns a tuple: (datetime object or None, is_all_day bool)
        """
        due = task.get('due', '')
        if not due:
            return None, False
        
        try:
            # New structured format: {date, time, all_day}
            if isinstance(due, dict):
                date_str = due.get('date', '')
                time_str = due.get('time', '')
                is_all_day = due.get('all_day', False)
                
                if is_all_day and date_str:
                    # Return date only for all-day events
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d"), True
                
                if date_str and time_str:
                    # Both date and time specified
                    dt_str = f"{date_str} {time_str}"
                    return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M"), False
                
                if date_str:
                    # Date only, not all-day
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d"), False
                
                return None, False
            
            # Old string format (legacy support)
            if isinstance(due, str):
                # Try parsing ISO format first
                if 'T' in due:
                    return datetime.datetime.fromisoformat(due.replace('Z', '+00:00')), False
                
                # Try parsing time only (HH:MM)
                if ':' in due and len(due) <= 5:
                    today = datetime.datetime.now().date()
                    time_parts = due.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    return datetime.datetime.combine(today, datetime.time(hour, minute)), False
            
        except Exception as e:
            print(f"[WARNING] Could not parse due date '{due}': {e}")
        
        return None, False
    
    def create_calendar_event(self, task):
        """
        Create a Google Calendar event from a task.
        
        Args:
            task: Dictionary containing task data
            
        Returns:
            Created event object or None if failed
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        action = task.get('action', 'Untitled Task')
        due_dt, is_all_day = self.parse_due_datetime(task)
        priority = task.get('priority', 'medium')
        transcript = task.get('transcript', '')
        
        # Determine event timing
        if due_dt and not is_all_day:
            # If we have a specific time, create a 30-minute event
            start_time = due_dt
            end_time = due_dt + datetime.timedelta(minutes=30)
            
            event = {
                'summary': f"[{priority.upper()}] {action}",
                'description': f"Priority: {priority}\n\nFrom voice note:\n{transcript}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Phoenix',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Phoenix',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
        elif due_dt and is_all_day:
            # All-day event with specific date
            event_date = due_dt.date()
            event = {
                'summary': f"[{priority.upper()}] {action}",
                'description': f"Priority: {priority}\n\nFrom voice note:\n{transcript}",
                'start': {
                    'date': event_date.isoformat(),
                },
                'end': {
                    'date': event_date.isoformat(),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
        else:
            # All-day task for today (fallback)
            today = datetime.date.today()
            event = {
                'summary': f"[{priority.upper()}] {action}",
                'description': f"Priority: {priority}\n\nFrom voice note:\n{transcript}",
                'start': {
                    'date': today.isoformat(),
                },
                'end': {
                    'date': today.isoformat(),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
        
        # Set color based on priority
        color_map = {
            'high': '11',    # Red
            'medium': '5',   # Yellow
            'low': '10',     # Green
        }
        event['colorId'] = color_map.get(priority, '5')
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            print(f"[OK] Created event: {action} (ID: {created_event['id']})")
            return created_event
            
        except HttpError as error:
            print(f"[ERROR] Error creating event for '{action}': {error}")
            return None
    
    def mark_task_synced(self, task):
        """Mark a task as synced to Google Calendar."""
        filename = task.get('_filename')
        if not filename:
            return
        
        filepath = Path(self.tasks_dir) / filename
        try:
            task['synced_to_calendar'] = True
            task['synced_at'] = datetime.datetime.now().isoformat()
            
            # Remove temporary filename field before saving
            task_copy = {k: v for k, v in task.items() if k != '_filename'}
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(task_copy, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[WARNING] Could not mark task as synced: {e}")
    
    def sync_all_tasks(self, force_resync: bool = False):
        """
        Sync all tasks from JSON files to Google Calendar.
        
        Args:
            force_resync: If True, sync even tasks already marked as synced
        """
        if not self.service:
            self.authenticate()
        
        tasks = self.load_tasks()
        
        if not tasks:
            print("No tasks to sync.")
            return
        
        synced_count = 0
        skipped_count = 0
        
        for task in tasks:
            # Skip if already synced (unless force_resync)
            if task.get('synced_to_calendar') and not force_resync:
                skipped_count += 1
                continue
            
            # Skip if marked as completed
            if task.get('completed'):
                skipped_count += 1
                continue
            
            # Create calendar event
            event = self.create_calendar_event(task)
            
            if event:
                self.mark_task_synced(task)
                synced_count += 1
        
        print(f"\n{'='*50}")
        print(f"Sync complete!")
        print(f"  [OK] Synced: {synced_count}")
        print(f"  [SKIP] Skipped: {skipped_count}")
        print(f"{'='*50}")
    
    def list_upcoming_events(self, max_results: int = 10):
        """List upcoming events from Google Calendar (for verification)."""
        if not self.service:
            self.authenticate()
        
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            print(f"\n{'='*50}")
            print(f"Upcoming {max_results} events:")
            print(f"{'='*50}")
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print('No upcoming events found.')
                return
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  • {start}: {event['summary']}")
            
        except HttpError as error:
            print(f"An error occurred: {error}")


def main():
    """Main function to run the sync."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync voice journal tasks to Google Calendar')
    parser.add_argument('--tasks-dir', default='tasks', help='Directory containing task JSON files')
    parser.add_argument('--credentials', default='credentials.json', help='Path to Google credentials file')
    parser.add_argument('--force', action='store_true', help='Force resync of already synced tasks')
    parser.add_argument('--list-events', action='store_true', help='List upcoming calendar events')
    
    args = parser.parse_args()
    
    # Initialize sync
    syncer = GoogleCalendarSync(
        tasks_dir=args.tasks_dir,
        credentials_file=args.credentials
    )
    
    try:
        # Authenticate
        syncer.authenticate()
        
        # List events if requested
        if args.list_events:
            syncer.list_upcoming_events()
            return
        
        # Sync tasks
        syncer.sync_all_tasks(force_resync=args.force)
        
        # Show upcoming events for verification
        syncer.list_upcoming_events(max_results=5)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()