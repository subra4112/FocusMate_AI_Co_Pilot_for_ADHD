#test_voice.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime, timedelta
from voice import VoiceTranscriber
from intent_emotion import EmotionTaskDetector
from google_calendar_sync import GoogleCalendarSync
from dotenv import load_dotenv
import queue
import os

load_dotenv()

class VoiceJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Journal")
        self.root.geometry("500x700")
        self.root.configure(bg="white")
        
        # Initialize components
        self.vt = VoiceTranscriber(diarize=False, tag_audio_events=True)
        self.detector = EmotionTaskDetector(model="gpt-4o-mini", tasks_dir="tasks")
        
        # Initialize Google Calendar sync (silent initialization)
        self.calendar_sync = None
        self.calendar_enabled = False
        try:
            self.calendar_sync = GoogleCalendarSync(tasks_dir="tasks")
            self.calendar_sync.authenticate()
            self.calendar_enabled = True
            print("[OK] Google Calendar sync enabled")
        except Exception as e:
            print(f"[INFO] Google Calendar sync disabled: {e}")
            print("[INFO] Tasks will only be saved locally")
        
        # Data storage
        self.tasks = []
        self.timeline_entries = []
        self.is_recording = False
        self.message_queue = queue.Queue()
        self.current_page = "home"
        
        # Create UI
        self.create_navbar()
        self.create_pages()
        self.show_page("home")
        
        # Start queue processor
        self.process_queue()
    
    def create_navbar(self):
        navbar = tk.Frame(self.root, bg="#4CAF50", height=70)
        navbar.pack(side=tk.BOTTOM, fill=tk.X)
        navbar.pack_propagate(False)
        
        # Home button
        home_btn = tk.Button(
            navbar, text="🏠\nHome", font=("Arial", 10),
            bg="#4CAF50", fg="white", bd=0, cursor="hand2",
            activebackground="#45a049",
            command=lambda: self.show_page("home")
        )
        home_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2)
        
        # Calendar button
        calendar_btn = tk.Button(
            navbar, text="📅\nCalendar", font=("Arial", 10),
            bg="#4CAF50", fg="white", bd=0, cursor="hand2",
            activebackground="#45a049",
            command=lambda: self.show_page("calendar")
        )
        calendar_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2)
        
        # Mail button
        mail_btn = tk.Button(
            navbar, text="✉️\nMail", font=("Arial", 10),
            bg="#4CAF50", fg="white", bd=0, cursor="hand2",
            activebackground="#45a049",
            command=lambda: self.show_page("mail")
        )
        mail_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2)
    
    def create_pages(self):
        # Container for all pages
        self.pages_container = tk.Frame(self.root, bg="white")
        self.pages_container.pack(fill=tk.BOTH, expand=True)
        
        # Home page
        self.home_page = tk.Frame(self.pages_container, bg="white")
        self.create_home_page()
        
        # Calendar page
        self.calendar_page = tk.Frame(self.pages_container, bg="white")
        self.create_calendar_page()
        
        # Mail page
        self.mail_page = tk.Frame(self.pages_container, bg="white")
        self.create_mail_page()
    
    def create_home_page(self):
        # Title
        title = tk.Label(
            self.home_page, text="Voice Journal",
            font=("Arial", 24, "bold"),
            bg="white", fg="#333"
        )
        title.pack(pady=(40, 20))
        
        # Microphone button (large and centered)
        self.mic_button = tk.Button(
            self.home_page, text="🎤", font=("Arial", 80),
            bg="#4CAF50", fg="white", activebackground="#45a049",
            width=3, height=1, bd=0, cursor="hand2",
            command=self.toggle_recording
        )
        self.mic_button.pack(pady=30)
        
        # Status label
        self.status_label = tk.Label(
            self.home_page, text="Tap to speak",
            font=("Arial", 14), bg="white", fg="#666"
        )
        self.status_label.pack(pady=10)
        
        # Transcription area
        trans_label = tk.Label(
            self.home_page, text="Transcript",
            font=("Arial", 12, "bold"), bg="white", fg="#333"
        )
        trans_label.pack(pady=(30, 10))
        
        self.transcription_text = scrolledtext.ScrolledText(
            self.home_page, height=12, font=("Arial", 11), wrap=tk.WORD,
            bg="#f9f9f9", relief=tk.FLAT, padx=10, pady=10
        )
        self.transcription_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    def create_calendar_page(self):
        # Title
        title = tk.Label(
            self.calendar_page,
            text=f"Tasks - {datetime.now().strftime('%b %d')}",
            font=("Arial", 20, "bold"), bg="white", fg="#333"
        )
        title.pack(pady=(30, 20))
        
        # Tasks frame
        tasks_frame = tk.Frame(self.calendar_page, bg="white")
        tasks_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Tasks listbox
        self.tasks_listbox = tk.Listbox(
            tasks_frame, font=("Arial", 11), bg="#f9f9f9", relief=tk.FLAT,
            selectmode=tk.SINGLE, activestyle="none"
        )
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tasks_frame, command=self.tasks_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        
        # Guidelines section
        guidelines_label = tk.Label(
            self.calendar_page, text="Calming Guidelines",
            font=("Arial", 12, "bold"), bg="white", fg="#333"
        )
        guidelines_label.pack(pady=(20, 10))
        
        self.guidelines_text = scrolledtext.ScrolledText(
            self.calendar_page, height=10, font=("Arial", 10), wrap=tk.WORD,
            bg="#fff8e1", relief=tk.FLAT, padx=10, pady=10
        )
        self.guidelines_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.guidelines_text.insert("1.0", "Guidelines will appear when needed...")
        self.guidelines_text.config(state=tk.DISABLED)
    
    def create_mail_page(self):
        # Title
        title = tk.Label(
            self.mail_page, text="Activity Timeline",
            font=("Arial", 20, "bold"), bg="white", fg="#333"
        )
        title.pack(pady=(30, 20))
        
        # Timeline
        self.timeline_text = scrolledtext.ScrolledText(
            self.mail_page, font=("Arial", 10), wrap=tk.WORD,
            bg="#f9f9f9", relief=tk.FLAT, padx=15, pady=15
        )
        self.timeline_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.timeline_text.insert("1.0", "Your activity will appear here...\n")
        self.timeline_text.config(state=tk.DISABLED)
    
    def show_page(self, page_name):
        # Hide all pages
        self.home_page.pack_forget()
        self.calendar_page.pack_forget()
        self.mail_page.pack_forget()
        
        # Show selected page
        if page_name == "home":
            self.home_page.pack(fill=tk.BOTH, expand=True)
        elif page_name == "calendar":
            self.calendar_page.pack(fill=tk.BOTH, expand=True)
            self.refresh_tasks()
        elif page_name == "mail":
            self.mail_page.pack(fill=tk.BOTH, expand=True)
            self.refresh_timeline()
        
        self.current_page = page_name
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.mic_button.config(bg="#f44336")
        self.status_label.config(text="Listening...", fg="#f44336")
        
        # Start recording in separate thread
        thread = threading.Thread(target=self.record_audio, daemon=True)
        thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.mic_button.config(bg="#4CAF50")
        self.status_label.config(text="Processing...", fg="#FF9800")
    
    def record_audio(self):
        try:
            # Record with voice activity detection - stops 5 seconds after silence
            text = self.vt.record_and_transcribe_vad(
                max_seconds=30.0,
                silence_duration=5.0,  # Stop after 5 seconds of silence
                silence_threshold=0.01
            )
            if text and text.strip():
                self.message_queue.put(("transcription", text))
                self.message_queue.put(("analyze", text))
            else:
                self.message_queue.put(("error", "No speech detected"))
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def sync_tasks_to_calendar(self, tasks):
        """Sync tasks to Google Calendar in background thread."""
        if not self.calendar_enabled or not self.calendar_sync:
            return
        
        def sync_worker():
            try:
                synced_count = 0
                for task in tasks:
                    # Create the event
                    event = self.calendar_sync.create_calendar_event(task)
                    if event:
                        synced_count += 1
                
                if synced_count > 0:
                    self.message_queue.put(("sync_success", synced_count))
            except Exception as e:
                print(f"[WARNING] Calendar sync failed: {e}")
                self.message_queue.put(("sync_error", str(e)))
        
        # Run sync in background thread
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
    
    def process_queue(self):
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                if msg_type == "transcription":
                    self.display_transcription(data)
                elif msg_type == "analyze":
                    self.analyze_and_display(data)
                elif msg_type == "error":
                    self.status_label.config(text=f"Error: {data}", fg="#f44336")
                    self.mic_button.config(bg="#4CAF50")
                elif msg_type == "sync_success":
                    count = data
                    status_msg = f"Synced {count} task(s) to Google Calendar"
                    print(f"[OK] {status_msg}")
                elif msg_type == "sync_error":
                    print(f"[WARNING] Calendar sync failed: {data}")
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
    
    def display_transcription(self, text):
        self.transcription_text.delete("1.0", tk.END)
        self.transcription_text.insert("1.0", text)
    
    def analyze_and_display(self, text):
        try:
            # Use the new analyze method with extract_all_tasks=True
            result = self.detector.analyze(text, include_guidelines=True, extract_all_tasks=True)
            
            # Add to timeline
            self.add_to_timeline(text, result)
            
            # Get extracted tasks from result (already saved to files in analyze())
            tasks = result.get("tasks", [])
            
            # Add each task to the UI calendar
            for task in tasks:
                self.add_task(task)
            
            # Sync tasks to Google Calendar (if enabled)
            if tasks:
                self.sync_tasks_to_calendar(tasks)
            
            # Display calming guidelines if needed
            emotion = result["emotion"]
            if "calming_guidelines" in result and emotion["primary"] != "joy":
                self.display_guidelines(result["calming_guidelines"], emotion["primary"])
            else:
                self.clear_guidelines()
            
            self.status_label.config(text="Tap to speak", fg="#4CAF50")
            self.mic_button.config(bg="#4CAF50")
            
        except Exception as e:
            self.message_queue.put(("error", f"Analysis failed: {str(e)}"))
    
    def add_task(self, task):
        timestamp = datetime.now()
        
        # Parse the due info (new structured format)
        due_info = task.get("due", {})
        
        # Handle both old string format and new dict format
        if isinstance(due_info, str):
            # Legacy format conversion
            if " " in due_info:
                try:
                    task_datetime = datetime.strptime(due_info, "%Y-%m-%d %H:%M")
                    date_str = task_datetime.strftime("%b %d") if task_datetime.date() != timestamp.date() else "Today"
                    time_str = task_datetime.strftime("%H:%M")
                except ValueError:
                    date_str = "Today"
                    time_str = timestamp.strftime("%H:%M")
            else:
                date_str = "Today"
                time_str = due_info if due_info else timestamp.strftime("%H:%M")
        else:
            # New structured format
            task_date = due_info.get("date", "")
            task_time = due_info.get("time", "")
            is_all_day = due_info.get("all_day", False)
            
            # Format date
            if task_date:
                try:
                    dt = datetime.strptime(task_date, "%Y-%m-%d")
                    if dt.date() == timestamp.date():
                        date_str = "Today"
                    elif dt.date() == (timestamp + timedelta(days=1)).date():
                        date_str = "Tomorrow"
                    else:
                        date_str = dt.strftime("%b %d")
                except ValueError:
                    date_str = "Today"
            else:
                date_str = "Today"
            
            # Format time
            if is_all_day:
                time_str = "All day"
            elif task_time:
                time_str = task_time
            else:
                time_str = timestamp.strftime("%H:%M")
        
        task_data = {
            "time": time_str,
            "date": date_str,
            "action": task["action"],
            "priority": task.get("priority", "medium"),
            "timestamp": timestamp
        }
        
        # Check for duplicates
        task_exists = any(
            t["action"].lower() == task_data["action"].lower() and 
            t["time"] == task_data["time"] and
            t["date"] == task_data["date"]
            for t in self.tasks
        )
        
        if not task_exists:
            self.tasks.append(task_data)
            # Sort by date first, then time (all-day events go first)
            self.tasks.sort(key=lambda x: (
                0 if x["date"] == "Today" else (1 if x["date"] == "Tomorrow" else 2),
                "00:00" if x["time"] == "All day" else x["time"]
            ))

    def refresh_tasks(self):
        self.tasks_listbox.delete(0, tk.END)
        if not self.tasks:
            self.tasks_listbox.insert(tk.END, "No tasks yet...")
            return
        
        for task in self.tasks:
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"], "⚪")
            
            # Build the display string
            parts = []
            
            # Add date if not today
            if task.get("date") != "Today":
                parts.append(task["date"])
            
            # Add time unless it's "All day"
            if task["time"] != "All day":
                parts.append(task["time"])
            
            # Combine date/time with action
            time_info = " ".join(parts)
            if time_info:
                task_line = f"{time_info} {priority_emoji} {task['action']}"
            else:
                task_line = f"{priority_emoji} {task['action']}"
            
            self.tasks_listbox.insert(tk.END, task_line)
    def add_to_timeline(self, text, result):
        timestamp = datetime.now().strftime("%H:%M:%S")
        emotion = result["emotion"]["primary"]
        entry = {"timestamp": timestamp, "text": text, "emotion": emotion}
        self.timeline_entries.append(entry)
        if len(self.timeline_entries) > 50:
            self.timeline_entries.pop(0)
    
    def refresh_timeline(self):
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete("1.0", tk.END)
        if not self.timeline_entries:
            self.timeline_text.insert("1.0", "Your activity will appear here...\n")
            self.timeline_text.config(state=tk.DISABLED)
            return
        
        emotion_emoji = {
            "joy": "😊", "sadness": "😢", "anger": "😠",
            "fear": "😨", "anxiety": "😰", "neutral": "😐"
        }
        
        for entry in reversed(self.timeline_entries):
            emoji = emotion_emoji.get(entry["emotion"], "💭")
            line = f"[{entry['timestamp']}] {emoji}\n{entry['text']}\n\n"
            self.timeline_text.insert(tk.END, line)
            self.timeline_text.insert(tk.END, "─" * 50 + "\n\n")
        
        self.timeline_text.config(state=tk.DISABLED)
    
    def display_guidelines(self, guidelines, emotion):
        self.guidelines_text.config(state=tk.NORMAL)
        self.guidelines_text.delete("1.0", tk.END)
        
        content = f"🧘 {emotion.upper()} SUPPORT\n\n"
        content += f"{guidelines['message']}\n\n"
        
        if "immediate" in guidelines:
            content += "⚡ DO NOW:\n"
            for i, technique in enumerate(guidelines["immediate"], 1):
                content += f"{i}. {technique}\n"
            content += "\n"
        
        if "strategies" in guidelines:
            content += "💡 STRATEGIES:\n"
            for i, strategy in enumerate(guidelines["strategies"], 1):
                content += f"{i}. {strategy}\n"
            content += "\n"
        
        if "professional_help" in guidelines:
            content += f"ℹ️ {guidelines['professional_help']}\n"
        
        self.guidelines_text.insert("1.0", content)
        self.guidelines_text.config(state=tk.DISABLED)
    
    def clear_guidelines(self):
        self.guidelines_text.config(state=tk.NORMAL)
        self.guidelines_text.delete("1.0", tk.END)
        self.guidelines_text.insert("1.0", "✅ You're doing great!\n\nNo regulation needed right now.")
        self.guidelines_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = VoiceJournalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()