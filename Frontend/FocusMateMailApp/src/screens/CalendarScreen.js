import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { Calendar } from "react-native-calendars";
import { Feather } from "@expo/vector-icons";
import { colors, radius, spacing, typography } from "../theme";
import { fetchCalendarEvents } from "../services/calendar";

const monthFormatter = new Intl.DateTimeFormat("en-US", {
  month: "long",
  year: "numeric",
});

const weekdayFormatter = new Intl.DateTimeFormat("en-US", {
  weekday: "long",
});

const timeFormatter = new Intl.DateTimeFormat("en-US", {
  hour: "numeric",
  minute: "2-digit",
});

function formatDateLabel(dateString) {
  const date = new Date(`${dateString}T00:00:00`);
  const day = weekdayFormatter.format(date);
  const monthDay = date.getDate();
  return `${day}, ${monthDay}`;
}

function formatTimeRange(startIso, endIso) {
  if (!startIso) {
    return "";
  }
  const startDate = new Date(startIso);
  const endDate = endIso ? new Date(endIso) : null;

  const startLabel = timeFormatter.format(startDate);
  const endLabel = endDate ? timeFormatter.format(endDate) : null;

  return endLabel ? `${startLabel} – ${endLabel}` : startLabel;
}

function eventKey(date) {
  return date?.split("T")[0];
}

function EventCard({ event, index }) {
  return (
    <View style={[styles.eventCard, index === 0 && styles.eventCardPrimary]}>
      <View style={styles.eventHeader}>
        <View style={styles.eventIndicator} />
        <View style={styles.eventHeaderText}>
          <Text style={styles.eventTitle}>{event.title}</Text>
          {event.category ? (
            <Text style={styles.eventCategory}>{event.category}</Text>
          ) : null}
        </View>
      </View>
      <View style={styles.eventMetaRow}>
        <Feather name="clock" size={16} color={colors.textSecondary} />
        <Text style={styles.eventMetaText}>
          {formatTimeRange(event.start, event.end)}
        </Text>
      </View>
      {event.location ? (
        <View style={styles.eventMetaRow}>
          <Feather name="map-pin" size={16} color={colors.textSecondary} />
          <Text style={styles.eventMetaText}>{event.location}</Text>
        </View>
      ) : null}
      {event.description ? (
        <Text style={styles.eventDescription}>{event.description}</Text>
      ) : null}
    </View>
  );
}

export function CalendarScreen() {
  const today = new Date().toISOString().split("T")[0];
  const [selectedDate, setSelectedDate] = useState(today);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const loadEvents = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) {
        setLoading(true);
      }
      setErrorMessage("");
      try {
        const data = await fetchCalendarEvents({});
        setEvents(data);
      } catch (error) {
        const readable = error?.message || "Unable to load calendar.";
        setErrorMessage(readable);
      } finally {
        if (!silent) {
          setLoading(false);
        }
        setRefreshing(false);
      }
    },
    []
  );

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const eventsByDate = useMemo(() => {
    const grouped = {};
    events.forEach((event) => {
      const key = eventKey(event.start);
      if (!key) {
        return;
      }
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(event);
    });
    Object.keys(grouped).forEach((key) => {
      grouped[key].sort(
        (a, b) => new Date(a.start).getTime() - new Date(b.start).getTime()
      );
    });
    return grouped;
  }, [events]);

  const markedDates = useMemo(() => {
    const marks = {};

    Object.entries(eventsByDate).forEach(([date, dayEvents]) => {
      marks[date] = {
        marked: dayEvents.length > 0,
        dotColor: colors.accentSoft,
      };
    });

    marks[selectedDate] = {
      ...(marks[selectedDate] || {}),
      selected: true,
      selectedColor: colors.accent,
      selectedTextColor: "#FFFFFF",
    };

    return marks;
  }, [eventsByDate, selectedDate]);

  const selectedEvents = eventsByDate[selectedDate] || [];
  const selectedDateObj = new Date(`${selectedDate}T00:00:00`);

  const handleDayPress = (day) => {
    setSelectedDate(day.dateString);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadEvents({ silent: true });
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={colors.accent}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.appTitle}>FocusMate</Text>
            <Text style={styles.monthLabel}>
              {monthFormatter.format(selectedDateObj)}
            </Text>
            <Text style={styles.dateLabel}>{formatDateLabel(selectedDate)}</Text>
          </View>

          <View style={styles.avatar}>
            <Feather name="user" size={20} color={colors.textPrimary} />
          </View>
        </View>

        <View style={styles.calendarWrapper}>
          <Calendar
            current={selectedDate}
            onDayPress={handleDayPress}
            markedDates={markedDates}
            theme={{
              backgroundColor: colors.surface,
              calendarBackground: colors.surface,
              textSectionTitleColor: colors.textMuted,
              selectedDayBackgroundColor: colors.accent,
              selectedDayTextColor: "#FFFFFF",
              todayTextColor: colors.accentSoft,
              dayTextColor: colors.textPrimary,
              monthTextColor: colors.textPrimary,
              arrowColor: colors.textPrimary,
              textDisabledColor: colors.textMuted,
            }}
            firstDay={1}
            enableSwipeMonths
          />
        </View>

        <View style={styles.agendaHeader}>
          <Text style={styles.agendaTitle}>Today’s Focus Blocks</Text>
          <Text style={styles.agendaSubtitle}>
            {selectedEvents.length > 0
              ? `${selectedEvents.length} scheduled`
              : "No events scheduled"}
          </Text>
        </View>

        {errorMessage ? (
          <View style={styles.errorBanner}>
            <Feather name="alert-triangle" size={16} color={colors.warning} />
            <Text style={styles.errorText}>{errorMessage}</Text>
          </View>
        ) : null}

        {loading ? (
          <View style={styles.loadingState}>
            <ActivityIndicator color={colors.accentSoft} />
            <Text style={styles.loadingLabel}>Loading your schedule…</Text>
          </View>
        ) : selectedEvents.length > 0 ? (
          selectedEvents.map((event, index) => (
            <EventCard key={event.id || index} event={event} index={index} />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Feather name="calendar" size={28} color={colors.textMuted} />
            <Text style={styles.emptyTitle}>Clear skies for now</Text>
            <Text style={styles.emptySubtitle}>
              No events scheduled — tap another day or plan your next focus
              block.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.xl * 1.2,
    gap: spacing.lg,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  appTitle: {
    fontSize: typography.heading1,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  monthLabel: {
    fontSize: typography.heading3,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  dateLabel: {
    fontSize: typography.body,
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.card,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.divider,
  },
  calendarWrapper: {
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.surface,
  },
  agendaHeader: {
    gap: spacing.xs,
  },
  agendaTitle: {
    fontSize: typography.heading2,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  agendaSubtitle: {
    fontSize: typography.small,
    color: colors.textMuted,
  },
  errorBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    padding: spacing.md,
    borderRadius: radius.md,
    backgroundColor: "rgba(249, 115, 22, 0.12)",
    borderWidth: 1,
    borderColor: colors.warning,
  },
  errorText: {
    flex: 1,
    color: colors.warning,
    fontSize: typography.small,
  },
  loadingState: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.xl,
    gap: spacing.sm,
  },
  loadingLabel: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
  eventCard: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    gap: spacing.sm,
    borderWidth: 1,
    borderColor: "rgba(79, 70, 229, 0.15)",
  },
  eventCardPrimary: {
    borderColor: "rgba(99, 102, 241, 0.35)",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
  eventHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  eventIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: colors.accent,
  },
  eventHeaderText: {
    flex: 1,
    gap: spacing.xs / 2,
  },
  eventTitle: {
    fontSize: typography.heading3,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  eventCategory: {
    fontSize: typography.micro,
    fontWeight: "600",
    color: colors.textSecondary,
    letterSpacing: 0.6,
    textTransform: "uppercase",
  },
  eventMetaRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  eventMetaText: {
    color: colors.textSecondary,
    fontSize: typography.small,
  },
  eventDescription: {
    color: colors.textMuted,
    fontSize: typography.small,
    lineHeight: 20,
  },
  emptyState: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.xl,
    gap: spacing.md,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  emptyTitle: {
    fontSize: typography.heading3,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  emptySubtitle: {
    color: colors.textMuted,
    fontSize: typography.small,
    textAlign: "center",
    paddingHorizontal: spacing.lg,
  },
});


