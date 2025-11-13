// Google Calendar Integration Service for FocusMate
// Works with your original JSON format

import moment from 'moment';

class GoogleCalendarService {
  constructor() {
    // TODO: Add your credentials from Google Cloud Console
    this.CLIENT_ID = '198933136997-1vclb3llqgf4p1un2kveqra1iadpjml6.apps.googleusercontent.com';
    this.API_KEY = 'AIzaSyBi9XjMZALb9Kknt0IgPM17rEoN15P2F4o';
    this.DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
    this.SCOPES = 'https://www.googleapis.com/auth/calendar.events';
    
    this.tokenClient = null;
    this.gapiInited = false;
    this.gisInited = false;
  }

  /**
   * Load Google API scripts
   */
  loadGoogleScripts() {
    return new Promise((resolve, reject) => {
      // Load GAPI script
      const gapiScript = document.createElement('script');
      gapiScript.src = 'https://apis.google.com/js/api.js';
      gapiScript.onload = () => {
        // Load GIS script
        const gisScript = document.createElement('script');
        gisScript.src = 'https://accounts.google.com/gsi/client';
        gisScript.onload = resolve;
        gisScript.onerror = reject;
        document.body.appendChild(gisScript);
      };
      gapiScript.onerror = reject;
      document.body.appendChild(gapiScript);
    });
  }

  /**
   * Initialize Google API Client
   */
  async initializeGapi() {
    return new Promise((resolve) => {
      gapi.load('client', async () => {
        await gapi.client.init({
          apiKey: this.API_KEY,
          discoveryDocs: [this.DISCOVERY_DOC],
        });
        this.gapiInited = true;
        console.log('✅ Google API initialized');
        resolve();
      });
    });
  }

  /**
   * Initialize Google Identity Services
   */
  initializeGis(callback) {
    this.tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: this.CLIENT_ID,
      scope: this.SCOPES,
      callback: callback,
    });
    this.gisInited = true;
    console.log('✅ Google Identity Services initialized');
  }

  /**
   * Check if user is signed in
   */
  isSignedIn() {
    return gapi?.client?.getToken() !== null;
  }

  /**
   * Sign in to Google Calendar
   */
  async signIn() {
    return new Promise((resolve, reject) => {
      if (!this.tokenClient) {
        reject('Token client not initialized');
        return;
      }

      this.tokenClient.callback = async (resp) => {
        if (resp.error !== undefined) {
          reject(resp);
          return;
        }
        console.log('✅ Signed in to Google Calendar');
        resolve();
      };

      if (gapi.client.getToken() === null) {
        this.tokenClient.requestAccessToken({prompt: 'consent'});
      } else {
        this.tokenClient.requestAccessToken({prompt: ''});
      }
    });
  }

  /**
   * Sign out from Google Calendar
   */
  signOut() {
    const token = gapi.client.getToken();
    if (token !== null) {
      google.accounts.oauth2.revoke(token.access_token);
      gapi.client.setToken('');
      console.log('✅ Signed out from Google Calendar');
    }
  }

  /**
   * Parse your task format and create proper datetime
   * Handles your format: { "due": "09:00", "created_at": "2025-11-09T14:16:43.947831" }
   */
  parseTaskDateTime(task) {
    // Get the date from created_at or use today
    const baseDate = task.created_at 
      ? moment(task.created_at).format('YYYY-MM-DD')
      : moment().format('YYYY-MM-DD');

    // If due is just time like "09:00", combine with date
    if (task.due && task.due.includes(':')) {
      return moment(`${baseDate}T${task.due}:00`).toISOString();
    }
    
    // If due is empty, use created_at or now
    return task.created_at || moment().toISOString();
  }

  /**
   * Calculate end time based on priority (your format doesn't have estimated_minutes)
   */
  calculateEndTime(startTime, priority) {
    const start = moment(startTime);
    
    // Duration based on priority
    const durations = {
      'high': 60,    // 1 hour for high priority
      'medium': 45,  // 45 mins for medium
      'low': 30      // 30 mins for low
    };
    
    const duration = durations[priority] || 30;
    return start.add(duration, 'minutes').toISOString();
  }

  /**
   * Get calendar color based on priority
   */
  getColorByPriority(priority) {
    const colors = {
      'high': '11',    // Red
      'medium': '5',   // Yellow
      'low': '2'       // Green
    };
    return colors[priority] || '1';
  }

  /**
   * Build event description from your task format
   */
  buildEventDescription(task) {
    let description = '';
    
    if (task.transcript) {
      description += `🎙️ From Voice: "${task.transcript}"\n\n`;
    }
    
    description += `📋 Priority: ${task.priority}\n`;
    description += `🤖 Confidence: ${(task.confidence * 100).toFixed(0)}%\n`;
    
    if (task.rationale) {
      description += `💡 Rationale: ${task.rationale}\n`;
    }
    
    description += `\n📱 Created via FocusMate`;
    
    return description;
  }

  /**
   * Create Google Calendar event from YOUR task format
   * @param {Object} task - Your task format with "due": "09:00"
   * @returns {Promise<string>} - Calendar event ID
   */
  async createEventFromTask(task) {
    try {
      if (!this.isSignedIn()) {
        throw new Error('Not signed in to Google Calendar');
      }

      // Parse the datetime from your format
      const startDateTime = this.parseTaskDateTime(task);
      const endDateTime = this.calculateEndTime(startDateTime, task.priority);

      const event = {
        summary: `${task.action}`,
        description: this.buildEventDescription(task),
        start: {
          dateTime: startDateTime,
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        },
        end: {
          dateTime: endDateTime,
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        },
        colorId: this.getColorByPriority(task.priority),
        reminders: {
          useDefault: false,
          overrides: [
            {method: 'popup', minutes: 30},
            {method: 'popup', minutes: 10},
          ],
        },
      };

      const response = await gapi.client.calendar.events.insert({
        calendarId: 'primary',
        resource: event,
      });

      console.log('✅ Calendar event created:', response.result.htmlLink);
      return response.result.id;
    } catch (error) {
      console.error('❌ Error creating calendar event:', error);
      throw error;
    }
  }

  /**
   * Create multiple events from task array
   */
  async createEventsFromTasks(tasks) {
    const results = [];
    
    for (const task of tasks) {
      try {
        const eventId = await this.createEventFromTask(task);
        results.push({
          taskId: task.id,
          eventId: eventId,
          success: true
        });
      } catch (error) {
        results.push({
          taskId: task.id,
          error: error.message,
          success: false
        });
      }
    }
    
    return results;
  }

  /**
   * Update event when task is marked complete
   */
  async markEventCompleted(eventId, task) {
    try {
      const event = await gapi.client.calendar.events.get({
        calendarId: 'primary',
        eventId: eventId,
      });

      // Update title with checkmark
      event.result.summary = `✅ ${task.action}`;
      event.result.colorId = '8'; // Gray for completed

      await gapi.client.calendar.events.update({
        calendarId: 'primary',
        eventId: eventId,
        resource: event.result,
      });

      console.log('✅ Event marked as completed');
    } catch (error) {
      console.error('❌ Error marking event complete:', error);
      throw error;
    }
  }

  /**
   * Delete a calendar event
   */
  async deleteEvent(eventId) {
    try {
      await gapi.client.calendar.events.delete({
        calendarId: 'primary',
        eventId: eventId,
      });
      console.log('✅ Event deleted');
    } catch (error) {
      console.error('❌ Error deleting event:', error);
      throw error;
    }
  }

  /**
   * Get upcoming events from Google Calendar
   */
  async getUpcomingEvents(maxResults = 50) {
    try {
      const response = await gapi.client.calendar.events.list({
        calendarId: 'primary',
        timeMin: (new Date()).toISOString(),
        showDeleted: false,
        singleEvents: true,
        maxResults: maxResults,
        orderBy: 'startTime',
      });

      return response.result.items;
    } catch (error) {
      console.error('❌ Error fetching events:', error);
      throw error;
    }
  }

  /**
   * Get events within a date range from Google Calendar
   */
  async getEventsInRange(startDate, endDate, maxResults = 100) {
    try {
      const response = await gapi.client.calendar.events.list({
        calendarId: 'primary',
        timeMin: startDate.toISOString(),
        timeMax: endDate.toISOString(),
        showDeleted: false,
        singleEvents: true,
        maxResults: maxResults,
        orderBy: 'startTime',
      });

      return response.result.items;
    } catch (error) {
      console.error('❌ Error fetching events:', error);
      throw error;
    }
  }

  /**
   * Convert Google Calendar event to FocusMate task format
   */
  convertEventToTask(event) {
    const startTime = event.start.dateTime || event.start.date;
    const endTime = event.end.dateTime || event.end.date;
    const startMoment = moment(startTime);
    const endMoment = moment(endTime);

    return {
      id: event.id,
      created_at: event.created,
      action: event.summary || 'Untitled Event',
      due_date: startMoment.format('YYYY-MM-DD'),
      due_time: event.start.dateTime ? startMoment.format('HH:mm') : null,
      due_datetime: startTime,
      estimated_minutes: endMoment.diff(startMoment, 'minutes'),
      calendar_event_id: event.id,
      scheduled_start: startTime,
      scheduled_end: endTime,
      priority: this.getPriorityFromColor(event.colorId),
      confidence: 1.0,
      rationale: 'Imported from Google Calendar',
      transcript: event.description || '',
      completed: false,
      status: 'todo',
      source: 'google_calendar' // Mark as imported from calendar
    };
  }

  /**
   * Get priority from Google Calendar color
   */
  getPriorityFromColor(colorId) {
    const colorMap = {
      '11': 'high',   // Red
      '5': 'medium',  // Yellow
      '2': 'low',     // Green
    };
    return colorMap[colorId] || 'medium';
  }

  /**
   * Sync all incomplete tasks to calendar
   */
  async syncTasksToCalendar(tasks) {
    const incompleteTasks = tasks.filter(task => !task.completed);
    const results = await this.createEventsFromTasks(incompleteTasks);
    
    const successCount = results.filter(r => r.success).length;
    const failCount = results.filter(r => !r.success).length;
    
    console.log(`✅ Synced ${successCount} tasks to calendar`);
    if (failCount > 0) {
      console.log(`⚠️ Failed to sync ${failCount} tasks`);
    }
    
    return results;
  }
}

// Export singleton instance
const calendarService = new GoogleCalendarService();
export default calendarService;
