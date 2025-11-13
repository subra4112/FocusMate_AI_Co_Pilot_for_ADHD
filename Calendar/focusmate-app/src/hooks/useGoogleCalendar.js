// Custom React Hook for Google Calendar Integration
import { useState, useEffect } from 'react';
import calendarService from '../services/googleCalendar';

export function useGoogleCalendar() {
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeCalendar();
  }, []);

  const initializeCalendar = async () => {
    try {
      setIsLoading(true);
      
      // Load Google scripts
      await calendarService.loadGoogleScripts();
      
      // Initialize GAPI
      await calendarService.initializeGapi();
      
      // Initialize GIS
      calendarService.initializeGis(() => {
        setIsSignedIn(calendarService.isSignedIn());
      });
      
      setIsSignedIn(calendarService.isSignedIn());
      setIsLoading(false);
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      console.error('Failed to initialize Google Calendar:', err);
    }
  };

  const signIn = async () => {
    try {
      setError(null);
      await calendarService.signIn();
      setIsSignedIn(true);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const signOut = () => {
    try {
      calendarService.signOut();
      setIsSignedIn(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const createEvent = async (task) => {
    try {
      setError(null);
      return await calendarService.createEventFromTask(task);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const syncTasks = async (tasks) => {
    try {
      setError(null);
      return await calendarService.syncTasksToCalendar(tasks);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const markComplete = async (eventId, task) => {
    try {
      setError(null);
      return await calendarService.markEventCompleted(eventId, task);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteEvent = async (eventId) => {
    try {
      setError(null);
      return await calendarService.deleteEvent(eventId);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const fetchEvents = async (startDate, endDate) => {
    try {
      setError(null);
      return await calendarService.getEventsInRange(startDate, endDate);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const fetchUpcoming = async (maxResults = 50) => {
    try {
      setError(null);
      return await calendarService.getUpcomingEvents(maxResults);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const convertEventToTask = (event) => {
    return calendarService.convertEventToTask(event);
  };

  return {
    isSignedIn,
    isLoading,
    error,
    signIn,
    signOut,
    createEvent,
    syncTasks,
    markComplete,
    deleteEvent,
    fetchEvents,
    fetchUpcoming,
    convertEventToTask,
  };
}
