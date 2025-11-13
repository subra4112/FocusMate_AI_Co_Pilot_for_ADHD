import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class TimelineViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Day Timeline Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'timeline': '#2c3e50',
            'focus': '#3498db',
            'work': '#2ecc71',
            'break': '#e74c3c',
            'completed': '#95a5a6',
            'current': '#f39c12',
            'ongoing': '#9b59b6',
            'text': '#2c3e50',
            'text_light': '#7f8c8d',
            'progress_bg': '#ecf0f1',
            'progress_fill': '#27ae60'
        }
        
        self.timeline_data = None
        # Use system local time
        self.current_time = datetime.now().astimezone()
        
        self.setup_ui()
        self.load_timeline()
        
        # Auto-refresh every minute
        self.auto_refresh()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Top bar with title and refresh button
        top_frame = tk.Frame(self.root, bg='#34495e', height=60)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame,
            text="📅 Your Day Timeline",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#34495e'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.time_label = tk.Label(
            top_frame,
            text="",
            font=('Arial', 12),
            fg='#ecf0f1',
            bg='#34495e'
        )
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        refresh_btn = tk.Button(
            top_frame,
            text="🔄 Refresh",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.load_timeline
        )
        refresh_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Main canvas with scrollbar
        canvas_frame = tk.Frame(self.root, bg=self.colors['bg'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
    def load_timeline(self):
        """Load timeline from JSON file."""
        try:
            timeline_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'day_timeline.json')
            
            if not os.path.exists(timeline_path):
                self.show_error("Timeline file not found. Please run the main script first.")
                return
            
            with open(timeline_path, 'r', encoding='utf-8') as f:
                self.timeline_data = json.load(f)
            
            # Debug: Print focus routine info
            if 'focus_routine_info' in self.timeline_data:
                print(f"\n🎯 Focus Routine Info:")
                print(f"   Included: {self.timeline_data['focus_routine_info']['included']}")
                print(f"   Reason: {self.timeline_data['focus_routine_info']['reason']}")
            
            # Debug: Print sections found
            if 'sections' in self.timeline_data:
                print(f"\n📋 Sections found: {len(self.timeline_data['sections'])}")
                for section in self.timeline_data['sections']:
                    section_type = section.get('section_type', 'unknown')
                    items_count = len(section.get('items', []))
                    print(f"   - {section_type}: {items_count} items")
            
            # Use system local time
        self.current_time = datetime.now().astimezone()
            self.update_time_display()
            self.render_timeline()
            
        except Exception as e:
            self.show_error(f"Error loading timeline: {e}")
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def update_time_display(self):
        """Update the current time display."""
        time_str = self.current_time.strftime('%I:%M %p - %A, %B %d, %Y')
        self.time_label.config(text=f"Current Time: {time_str}")
    
    def parse_time_to_datetime(self, time_str):
        """Parse time string (HH:MM AM/PM) to datetime object for today."""
        try:
            time_obj = datetime.strptime(time_str.strip(), '%I:%M %p')
            return self.current_time.replace(
                hour=time_obj.hour,
                minute=time_obj.minute,
                second=0,
                microsecond=0
            )
        except:
            return None
    
    def get_task_status(self, start_time_str, end_time_str):
        """
        Determine if a task is past, ongoing, or future.
        Returns: ('past', None), ('ongoing', progress_percent), or ('future', None)
        """
        start_dt = self.parse_time_to_datetime(start_time_str)
        end_dt = self.parse_time_to_datetime(end_time_str)
        
        if not start_dt or not end_dt:
            return ('unknown', None)
        
        if self.current_time < start_dt:
            return ('future', None)
        elif self.current_time > end_dt:
            return ('past', None)
        else:
            # Ongoing - calculate progress
            total_duration = (end_dt - start_dt).total_seconds()
            elapsed = (self.current_time - start_dt).total_seconds()
            progress = (elapsed / total_duration) * 100 if total_duration > 0 else 0
            return ('ongoing', min(100, max(0, progress)))
    
    def get_segment_status(self, segment):
        """Get status for a specific segment."""
        return self.get_task_status(segment['start'], segment['end'])
    
    def show_error(self, message):
        """Show error message."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        error_label = tk.Label(
            self.scrollable_frame,
            text=f"⚠️ {message}",
            font=('Arial', 14),
            fg='#e74c3c',
            bg='white',
            pady=50
        )
        error_label.pack()
    
    def render_timeline(self):
        """Render the complete timeline."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.timeline_data or 'sections' not in self.timeline_data:
            self.show_error("No timeline data available")
            return
        
        y_position = 20
        
        # Display focus routine info banner if available
        if 'focus_routine_info' in self.timeline_data:
            self.render_focus_info_banner(self.timeline_data['focus_routine_info'])
            y_position += 80
        
        # Render each section
        for section in self.timeline_data['sections']:
            if section['section_type'] == 'focus_routine':
                y_position = self.render_focus_routine(section, y_position)
            elif section['section_type'] == 'work_schedule':
                y_position = self.render_work_schedule(section, y_position)
            
            y_position += 30  # Space between sections
        
        # Add summary footer
        self.render_summary_footer()
    
    def render_focus_info_banner(self, focus_info):
        """Render an information banner about focus routine inclusion."""
        # Make the banner more prominent when focus routine is included
        if focus_info['included']:
            bg_color = '#fff3cd'  # Brighter yellow
            border_color = '#ffc107'
            border_width = 2
        else:
            bg_color = '#d1ecf1'  # Light blue
            border_color = '#bee5eb'
            border_width = 1
        
        banner_frame = tk.Frame(
            self.scrollable_frame,
            bg=bg_color,
            relief=tk.SOLID,
            bd=border_width,
            highlightbackground=border_color,
            highlightthickness=2 if focus_info['included'] else 0
        )
        banner_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        icon = "🎯" if focus_info['included'] else "ℹ️"
        
        # Check if multiple focus routines
        count = focus_info.get('count', 1 if focus_info['included'] else 0)
        if count > 1:
            title = f"⭐ {count} FOCUS ROUTINES INCLUDED"
        elif count == 1:
            title = "⭐ FOCUS ROUTINE INCLUDED"
        else:
            title = "No Focus Routine"
        
        title_label = tk.Label(
            banner_frame,
            text=f"{icon} {title}",
            font=('Arial', 14, 'bold'),
            fg='#856404' if focus_info['included'] else self.colors['text'],
            bg=bg_color,
            anchor='w'
        )
        title_label.pack(fill=tk.X, padx=15, pady=(12, 5))
        
        reason_label = tk.Label(
            banner_frame,
            text=f"📝 Reason: {focus_info['reason']}",
            font=('Arial', 11),
            fg=self.colors['text'],
            bg=bg_color,
            anchor='w'
        )
        reason_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        if focus_info['included']:
            duration_label = tk.Label(
                banner_frame,
                text=f"⏱️  Max Duration: {focus_info['max_duration_minutes']} minutes",
                font=('Arial', 10, 'bold'),
                fg=self.colors['focus'],
                bg=bg_color,
                anchor='w'
            )
            duration_label.pack(fill=tk.X, padx=15, pady=(0, 12))
        else:
            note_label = tk.Label(
                banner_frame,
                text="💡 Focus routines are only added for: (1) First task of the day, or (2) After 4+ hour gaps",
                font=('Arial', 9, 'italic'),
                fg=self.colors['text_light'],
                bg=bg_color,
                anchor='w',
                wraplength=1100
            )
            note_label.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    def render_focus_routine(self, section, start_y):
        """Render focus routine section."""
        # Section header with prominent styling
        header_frame = tk.Frame(
            self.scrollable_frame, 
            bg='#e3f2fd',
            relief=tk.SOLID,
            bd=1
        )
        header_frame.pack(fill=tk.X, pady=(10, 5), padx=20)
        
        # Timeline marker
        timeline_canvas = tk.Canvas(
            header_frame,
            width=100,
            height=50,
            bg='#e3f2fd',
            highlightthickness=0
        )
        timeline_canvas.pack(side=tk.LEFT, padx=20)
        
        # Draw prominent circle marker
        timeline_canvas.create_oval(30, 10, 60, 40, fill=self.colors['focus'], outline=self.colors['focus'], width=3)
        timeline_canvas.create_text(45, 25, text="🎯", font=('Arial', 16))
        
        # Header text with emphasis
        header_content = tk.Frame(header_frame, bg='#e3f2fd')
        header_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        header_label = tk.Label(
            header_content,
            text="⭐ " + section['title'],
            font=('Arial', 18, 'bold'),
            fg=self.colors['focus'],
            bg='#e3f2fd',
            anchor='w'
        )
        header_label.pack(fill=tk.X)
        
        # Add task info if available
        if 'for_task' in section and 'task_start_time' in section:
            task_info = tk.Label(
                header_content,
                text=f"📌 For task: {section['for_task']} at {section['task_start_time']}",
                font=('Arial', 11),
                fg=self.colors['text'],
                bg='#e3f2fd',
                anchor='w'
            )
            task_info.pack(fill=tk.X, pady=(3, 0))
        
        # Add reason if available
        if 'reason' in section:
            reason_label = tk.Label(
                header_content,
                text=f"💡 {section['reason']}",
                font=('Arial', 10, 'italic'),
                fg=self.colors['text_light'],
                bg='#e3f2fd',
                anchor='w'
            )
            reason_label.pack(fill=tk.X, pady=(2, 0))
        
        # Add max duration info if available
        if 'max_duration' in section:
            duration_info = tk.Label(
                header_content,
                text=f"⏱️ Duration: {section['max_duration']}",
                font=('Arial', 10, 'italic'),
                fg=self.colors['text_light'],
                bg='#e3f2fd',
                anchor='w'
            )
            duration_info.pack(fill=tk.X, pady=(2, 0))
        
        # Render focus routine items
        for i, item in enumerate(section['items']):
            self.render_focus_item(item, i == len(section['items']) - 1)
        
        return start_y + 100
    
    def render_focus_item(self, item, is_last):
        """Render a single focus routine item."""
        # Get status of this focus item
        time_str = item['time']
        duration = item['duration_minutes']
        start_dt = self.parse_time_to_datetime(time_str)
        
        status = 'future'
        progress = None
        if start_dt:
            end_dt = start_dt + timedelta(minutes=duration)
            end_time_str = end_dt.strftime('%I:%M %p')
            status, progress = self.get_task_status(time_str, end_time_str)
        
        item_frame = tk.Frame(self.scrollable_frame, bg='white')
        item_frame.pack(fill=tk.X, pady=2)
        
        # Timeline section
        timeline_frame = tk.Frame(item_frame, width=100, bg='white')
        timeline_frame.pack(side=tk.LEFT, fill=tk.Y)
        timeline_frame.pack_propagate(False)
        
        timeline_canvas = tk.Canvas(
            timeline_frame,
            width=100,
            bg='white',
            highlightthickness=0
        )
        timeline_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Determine color based on status
        if status == 'past':
            line_color = self.colors['completed']
            marker_color = self.colors['completed']
        elif status == 'ongoing':
            line_color = self.colors['ongoing']
            marker_color = self.colors['ongoing']
        else:
            line_color = self.colors['focus']
            marker_color = self.colors['focus']
        
        # Draw vertical line
        if not is_last:
            timeline_canvas.create_line(45, 0, 45, 200, fill=line_color, width=2, dash=(5, 3))
        
        # Draw time marker with pulse effect for ongoing
        if status == 'ongoing':
            # Outer pulse circle
            timeline_canvas.create_oval(35, 15, 55, 35, fill='', outline=self.colors['ongoing'], width=3)
            timeline_canvas.create_oval(40, 20, 50, 30, fill=self.colors['ongoing'], outline='white', width=2)
        else:
            timeline_canvas.create_oval(40, 20, 50, 30, fill=marker_color, outline='white', width=2)
        
        # Time text with status
        time_display = item['time']
        if status == 'ongoing':
            time_display += "\n⏳ NOW"
        elif status == 'past':
            time_display += "\n✓"
        
        time_label = tk.Label(
            timeline_frame,
            text=time_display,
            font=('Arial', 9, 'bold'),
            fg=marker_color,
            bg='white'
        )
        time_label.place(x=10, y=40)
        
        # Content card with status-based styling
        if status == 'ongoing':
            bg_color = '#f4ecf7'
            border_width = 3
        elif status == 'past':
            bg_color = '#f2f3f4'
            border_width = 1
        else:
            bg_color = '#ebf5fb'
            border_width = 1
        
        content_frame = tk.Frame(
            item_frame,
            bg=bg_color,
            relief=tk.SOLID,
            bd=border_width,
            highlightbackground=marker_color,
            highlightthickness=2 if status == 'ongoing' else 0
        )
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=5)
        
        # Activity title with status indicator
        status_icon = ""
        if status == 'ongoing':
            status_icon = "⏳ IN PROGRESS "
        elif status == 'past':
            status_icon = "✅ "
        
        activity_label = tk.Label(
            content_frame,
            text=f"{status_icon}⏱️ {item['activity']} ({item['duration_minutes']} min)",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text'],
            bg=bg_color,
            anchor='w'
        )
        activity_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Progress bar for ongoing tasks
        if status == 'ongoing' and progress is not None:
            progress_frame = tk.Frame(content_frame, bg=bg_color)
            progress_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
            
            # Progress bar background
            progress_bg = tk.Canvas(
                progress_frame,
                height=25,
                bg=self.colors['progress_bg'],
                highlightthickness=0
            )
            progress_bg.pack(fill=tk.X)
            
            # Progress bar fill
            bar_width = progress_bg.winfo_reqwidth() if progress_bg.winfo_reqwidth() > 0 else 870
            fill_width = int(bar_width * (progress / 100))
            progress_bg.create_rectangle(
                0, 0, fill_width, 25,
                fill=self.colors['ongoing'],
                outline=''
            )
            
            # Progress text
            progress_bg.create_text(
                bar_width // 2, 12,
                text=f"{progress:.1f}% Complete",
                font=('Arial', 10, 'bold'),
                fill='white' if progress > 50 else self.colors['text']
            )
        
        # Description
        desc_label = tk.Label(
            content_frame,
            text=f"📋 {item['description']}",
            font=('Arial', 10),
            fg=self.colors['text'],
            bg=bg_color,
            anchor='w',
            wraplength=900,
            justify=tk.LEFT
        )
        desc_label.pack(fill=tk.X, padx=15, pady=3)
        
        # Purpose
        purpose_label = tk.Label(
            content_frame,
            text=f"💡 {item['purpose']}",
            font=('Arial', 10, 'italic'),
            fg=self.colors['text_light'],
            bg=bg_color,
            anchor='w',
            wraplength=900,
            justify=tk.LEFT
        )
        purpose_label.pack(fill=tk.X, padx=15, pady=(3, 10))
    
    def render_work_schedule(self, section, start_y):
        """Render work schedule section."""
        # Section header
        header_frame = tk.Frame(self.scrollable_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        # Timeline marker
        timeline_canvas = tk.Canvas(
            header_frame,
            width=100,
            height=40,
            bg='white',
            highlightthickness=0
        )
        timeline_canvas.pack(side=tk.LEFT, padx=20)
        
        # Draw circle marker
        timeline_canvas.create_oval(35, 15, 55, 35, fill=self.colors['work'], outline=self.colors['work'], width=3)
        timeline_canvas.create_text(45, 25, text="💼", font=('Arial', 12))
        
        # Header text
        header_label = tk.Label(
            header_frame,
            text=section['title'],
            font=('Arial', 16, 'bold'),
            fg=self.colors['work'],
            bg='white',
            anchor='w'
        )
        header_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Render work items
        for i, item in enumerate(section['items']):
            self.render_work_item(item, i == len(section['items']) - 1)
        
        return start_y + 100
    
    def render_work_item(self, item, is_last):
        """Render a single work schedule item."""
        is_past = item.get('is_past', False)
        
        # Main task header
        task_frame = tk.Frame(self.scrollable_frame, bg='white')
        task_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Timeline section
        timeline_frame = tk.Frame(task_frame, width=100, bg='white')
        timeline_frame.pack(side=tk.LEFT, fill=tk.Y)
        timeline_frame.pack_propagate(False)
        
        timeline_canvas = tk.Canvas(
            timeline_frame,
            width=100,
            bg='white',
            highlightthickness=0
        )
        timeline_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw vertical line
        if not is_last:
            color = self.colors['completed'] if is_past else self.colors['timeline']
            timeline_canvas.create_line(45, 0, 45, 400, fill=color, width=3)
        
        # Task header card
        header_bg = '#d5dbdb' if is_past else '#2c3e50'
        header_fg = '#7f8c8d' if is_past else 'white'
        
        task_header = tk.Frame(
            task_frame,
            bg=header_bg,
            relief=tk.FLAT
        )
        task_header.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 20))
        
        # Task title with status
        status_icon = "✅" if is_past else "🔜"
        status_text = "[COMPLETED]" if is_past else ""
        
        title_label = tk.Label(
            task_header,
            text=f"{status_icon} {item['original_task']} {status_text}",
            font=('Arial', 13, 'bold'),
            fg=header_fg,
            bg=header_bg,
            anchor='w'
        )
        title_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Time range
        time_label = tk.Label(
            task_header,
            text=f"🕐 {item['start']} - {item['end']}",
            font=('Arial', 11),
            fg=header_fg,
            bg=header_bg,
            anchor='w'
        )
        time_label.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Render segments
        for seg_idx, segment in enumerate(item['segments']):
            is_last_segment = seg_idx == len(item['segments']) - 1
            self.render_segment(segment, is_past, is_last_segment)
    
    def render_segment(self, segment, parent_is_past, is_last_segment):
        """Render a work or break segment with progress tracking."""
        # Get segment status
        status, progress = self.get_segment_status(segment)
        
        # Override with parent status if parent is past
        if parent_is_past:
            status = 'past'
            progress = None
        
        segment_frame = tk.Frame(self.scrollable_frame, bg='white')
        segment_frame.pack(fill=tk.X, pady=2)
        
        # Timeline section
        timeline_frame = tk.Frame(segment_frame, width=100, bg='white')
        timeline_frame.pack(side=tk.LEFT, fill=tk.Y)
        timeline_frame.pack_propagate(False)
        
        timeline_canvas = tk.Canvas(
            timeline_frame,
            width=100,
            height=120 if progress is None else 140,
            bg='white',
            highlightthickness=0
        )
        timeline_canvas.pack()
        
        # Determine colors based on status
        if segment['type'] == 'work':
            base_color = self.colors['work']
        else:
            base_color = self.colors['break']
        
        if status == 'past':
            line_color = self.colors['completed']
            marker_color = self.colors['completed']
        elif status == 'ongoing':
            line_color = self.colors['ongoing']
            marker_color = self.colors['ongoing']
        else:
            line_color = self.colors['timeline']
            marker_color = base_color
        
        # Draw connecting line
        if not is_last_segment:
            timeline_canvas.create_line(45, 0, 45, 120 if progress is None else 140, fill=line_color, width=3)
        
        # Draw segment marker with ongoing indicator
        if status == 'ongoing':
            # Pulsing effect for ongoing
            timeline_canvas.create_oval(35, 22, 55, 42, fill='', outline=marker_color, width=3)
            timeline_canvas.create_oval(38, 25, 52, 39, fill=marker_color, outline='white', width=2)
            icon_y = 32
        else:
            timeline_canvas.create_oval(38, 25, 52, 39, fill=marker_color, outline='white', width=2)
            icon_y = 32
        
        # Icon based on segment type and status
        if segment['type'] == 'work':
            if status == 'ongoing':
                icon = "⏳"
            elif status == 'past':
                icon = "✓"
            else:
                icon = "▶️"
        else:
            icon = "☕"
        
        # Time text with status
        time_text = f"{segment['start']}\n{segment['end']}"
        if status == 'ongoing':
            time_text += "\n⏳ NOW"
        elif status == 'past':
            time_text += "\n✓"
        
        timeline_canvas.create_text(45, 65, text=time_text, font=('Arial', 8), fill=marker_color)
        
        # Content card styling based on status
        if status == 'ongoing':
            if segment['type'] == 'work':
                bg_color = '#f4ecf7'  # Purple tint
            else:
                bg_color = '#fdecea'  # Red tint
            border_width = 3
        elif status == 'past':
            bg_color = '#f2f3f4'
            border_width = 1
        else:
            if segment['type'] == 'work':
                bg_color = '#e8f8f5'
            else:
                bg_color = '#fadbd8'
            border_width = 1
        
        border_color = marker_color
        
        content_frame = tk.Frame(
            segment_frame,
            bg=bg_color,
            relief=tk.SOLID,
            bd=border_width,
            highlightbackground=border_color,
            highlightthickness=3 if status == 'ongoing' else 1
        )
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=5)
        
        if segment['type'] == 'work':
            # Work segment
            status_prefix = ""
            if status == 'ongoing':
                status_prefix = "⏳ IN PROGRESS - "
            elif status == 'past':
                status_prefix = "✅ "
            
            label_text = f"{status_prefix}💼 WORK: {segment['activity']}"
            label = tk.Label(
                content_frame,
                text=label_text,
                font=('Arial', 11, 'bold'),
                fg=self.colors['text'],
                bg=bg_color,
                anchor='w'
            )
            label.pack(fill=tk.X, padx=15, pady=10)
            
        else:
            # Break segment
            status_prefix = ""
            if status == 'ongoing':
                status_prefix = "⏳ TAKING BREAK - "
            elif status == 'past':
                status_prefix = "✅ "
            
            duration_text = f"{status_prefix}☕ BREAK ({segment['duration_minutes']} min)"
            duration_label = tk.Label(
                content_frame,
                text=duration_text,
                font=('Arial', 11, 'bold'),
                fg=self.colors['text'],
                bg=bg_color,
                anchor='w'
            )
            duration_label.pack(fill=tk.X, padx=15, pady=(10, 3))
            
            # Activity
            activity_label = tk.Label(
                content_frame,
                text=f"Activity: {segment['activity']}",
                font=('Arial', 10),
                fg=self.colors['text'],
                bg=bg_color,
                anchor='w'
            )
            activity_label.pack(fill=tk.X, padx=15, pady=2)
            
            # Reason
            reason_label = tk.Label(
                content_frame,
                text=f"Reason: {segment['reason']}",
                font=('Arial', 10, 'italic'),
                fg=self.colors['text_light'],
                bg=bg_color,
                anchor='w',
                wraplength=900,
                justify=tk.LEFT
            )
            reason_label.pack(fill=tk.X, padx=15, pady=(2, 5))
        
        # Add progress bar for ongoing segments
        if status == 'ongoing' and progress is not None:
            progress_frame = tk.Frame(content_frame, bg=bg_color)
            progress_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
            
            # Progress bar background
            progress_bg = tk.Canvas(
                progress_frame,
                height=25,
                bg=self.colors['progress_bg'],
                highlightthickness=0
            )
            progress_bg.pack(fill=tk.X)
            
            # Calculate bar dimensions
            bar_width = 870  # Approximate width
            fill_width = int(bar_width * (progress / 100))
            
            # Progress bar fill
            progress_bg.create_rectangle(
                0, 0, fill_width, 25,
                fill=marker_color,
                outline=''
            )
            
            # Progress text
            progress_bg.create_text(
                bar_width // 2, 12,
                text=f"{progress:.1f}% Complete",
                font=('Arial', 10, 'bold'),
                fill='white' if progress > 50 else self.colors['text']
            )
    
    def render_summary_footer(self):
        """Render a summary footer with key information."""
        footer_frame = tk.Frame(
            self.scrollable_frame,
            bg='#f8f9fa',
            relief=tk.SOLID,
            bd=1
        )
        footer_frame.pack(fill=tk.X, padx=20, pady=(20, 30))
        
        # Title
        title_label = tk.Label(
            footer_frame,
            text="📊 Timeline Summary",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text'],
            bg='#f8f9fa',
            anchor='w'
        )
        title_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Count sections
        focus_count = 0
        work_count = 0
        completed_count = 0
        ongoing_count = 0
        upcoming_count = 0
        
        for section in self.timeline_data.get('sections', []):
            if section['section_type'] == 'focus_routine':
                focus_count = len(section.get('items', []))
            elif section['section_type'] == 'work_schedule':
                work_count = len(section.get('items', []))
                for item in section.get('items', []):
                    if item.get('is_past'):
                        completed_count += 1
                    else:
                        # Check if ongoing
                        status, _ = self.get_task_status(item['start'], item['end'])
                        if status == 'ongoing':
                            ongoing_count += 1
                        else:
                            upcoming_count += 1
        
        # Display stats
        stats_text = f"✅ Completed Tasks: {completed_count}  |  ⏳ Ongoing: {ongoing_count}  |  🔜 Upcoming: {upcoming_count}"
        if focus_count > 0:
            stats_text += f"  |  🎯 Focus Steps: {focus_count}"
        
        stats_label = tk.Label(
            footer_frame,
            text=stats_text,
            font=('Arial', 11),
            fg=self.colors['text'],
            bg='#f8f9fa',
            anchor='w'
        )
        stats_label.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Focus routine status
        if 'focus_routine_info' in self.timeline_data:
            focus_info = self.timeline_data['focus_routine_info']
            if focus_info['included']:
                focus_status = tk.Label(
                    footer_frame,
                    text="🎯 Focus Routine: ✅ ACTIVE - Use this to get into the zone!",
                    font=('Arial', 10, 'bold'),
                    fg='#28a745',
                    bg='#f8f9fa',
                    anchor='w'
                )
            else:
                focus_status = tk.Label(
                    footer_frame,
                    text="ℹ️  Focus Routine: Not needed (continuous work schedule)",
                    font=('Arial', 10),
                    fg=self.colors['text_light'],
                    bg='#f8f9fa',
                    anchor='w'
                )
            focus_status.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    def auto_refresh(self):
        """Auto-refresh the timeline every minute."""
        # Use system local time
        self.current_time = datetime.now().astimezone()
        self.update_time_display()
        
        # Schedule next refresh in 60 seconds
        self.root.after(60000, self.auto_refresh)


def main():
    root = tk.Tk()
    app = TimelineViewer(root)
    root.mainloop()


if __name__ == '__main__':
    main()