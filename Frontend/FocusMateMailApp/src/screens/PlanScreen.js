import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, radius, typography } from "../theme";
import { fetchTimeline } from "../services/timeline";

export const PlanScreen = () => {
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [completedItems, setCompletedItems] = useState(new Set());

  useEffect(() => {
    loadTimeline();
  }, []);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      const data = await fetchTimeline();
      setTimeline(data);
    } catch (error) {
      console.error("Error loading timeline:", error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTimeline();
    setRefreshing(false);
  };

  const toggleComplete = (itemId) => {
    setCompletedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const calculateMomentum = () => {
    if (!timeline) return 0;
    
    let totalItems = 0;
    let completedCount = completedItems.size;

    timeline.sections?.forEach((section) => {
      if (section.section_type === "focus_routine") {
        totalItems += section.items?.length || 0;
      } else if (section.section_type === "work_schedule") {
        section.items?.forEach((task) => {
          if (!task.is_past) {
            totalItems += 1;
          }
        });
      }
    });

    return totalItems > 0 ? Math.round((completedCount / totalItems) * 100) : 0;
  };

  const parseTime = (timeStr) => {
    try {
      const [time, period] = timeStr.split(" ");
      const [hours, minutes] = time.split(":");
      return { hours, minutes, period };
    } catch {
      return { hours: "00", minutes: "00", period: "AM" };
    }
  };

  const calculateDuration = (startTime, endTime) => {
    try {
      const parseTimeToMinutes = (timeStr) => {
        const [time, period] = timeStr.split(" ");
        let [hours, minutes] = time.split(":").map(Number);
        if (period === "PM" && hours !== 12) hours += 12;
        if (period === "AM" && hours === 12) hours = 0;
        return hours * 60 + minutes;
      };

      const start = parseTimeToMinutes(startTime);
      const end = parseTimeToMinutes(endTime);
      const diff = end >= start ? end - start : (24 * 60 - start) + end;
      return diff;
    } catch {
      return 0;
    }
  };

  const getEnergyLevel = (timeStr) => {
    try {
      const hour = parseInt(timeStr.split(":")[0]);
      const period = timeStr.split(" ")[1];
      const hour24 = period === "PM" && hour !== 12 ? hour + 12 : hour === 12 && period === "AM" ? 0 : hour;
      
      if (hour24 >= 6 && hour24 < 10) return "Low Energy";
      if (hour24 >= 10 && hour24 < 14) return "High Energy";
      if (hour24 >= 14 && hour24 < 18) return "Medium Energy";
      return "Low Energy";
    } catch {
      return "Medium Energy";
    }
  };

  const renderFocusRoutine = (section, sectionIndex) => {
    return (
      <View key={`focus-${sectionIndex}`} style={styles.section}>
        <View style={styles.sectionHeader}>
          <Feather name="target" size={20} color={colors.accent} />
          <Text style={styles.sectionTitle}>Focus Preparation</Text>
        </View>

        {section.items?.map((item, index) => {
          const itemId = `focus-${sectionIndex}-${index}`;
          const isCompleted = completedItems.has(itemId);
          const { hours, minutes } = parseTime(item.time);
          const energyLevel = getEnergyLevel(item.time);

          return (
            <View key={itemId} style={styles.timelineItem}>
              <View style={styles.timeColumn}>
                <Text style={styles.timeText}>
                  {hours}:{minutes}
                </Text>
                <Text style={styles.durationText}>{item.duration_minutes} min</Text>
              </View>

              <View style={styles.timelineLine}>
                <View
                  style={[
                    styles.timelineDot,
                    isCompleted && styles.timelineDotCompleted,
                  ]}
                />
                {index < section.items.length - 1 && <View style={styles.verticalLine} />}
              </View>

              <View style={styles.cardContainer}>
                <View
                  style={[
                    styles.activityCard,
                    isCompleted && styles.activityCardCompleted,
                  ]}
                >
                  <Text style={styles.activityTitle}>{item.activity}</Text>

                  <View style={styles.tagsRow}>
                    <View style={styles.tag}>
                      <Feather name="zap" size={12} color={colors.warning} />
                      <Text style={styles.tagText}>{energyLevel}</Text>
                    </View>
                    <View style={[styles.tag, styles.tagMindful]}>
                      <Feather name="circle" size={12} color={colors.accent} />
                      <Text style={styles.tagText}>Mindful</Text>
                    </View>
                  </View>

                  <Text style={styles.activityDescription}>
                    {item.description}
                  </Text>

                  <TouchableOpacity
                    style={[
                      styles.completeButton,
                      isCompleted && styles.completeButtonDone,
                    ]}
                    onPress={() => toggleComplete(itemId)}
                  >
                    <Feather
                      name={isCompleted ? "check-circle" : "circle"}
                      size={20}
                      color={isCompleted ? colors.success : colors.textMuted}
                    />
                    <Text
                      style={[
                        styles.completeButtonText,
                        isCompleted && styles.completeButtonTextDone,
                      ]}
                    >
                      {isCompleted ? "Completed" : "Tap to complete"}
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          );
        })}
      </View>
    );
  };

  const renderWorkSchedule = (section, sectionIndex) => {
    const filteredItems = section.items?.filter((item) => !item.is_past) || [];

    return (
      <View key={`work-${sectionIndex}`} style={styles.section}>
        {filteredItems.map((task, index) => {
          const itemId = `work-${task.event_id}`;
          const isCompleted = completedItems.has(itemId);
          const { hours, minutes } = parseTime(task.start);
          const duration = calculateDuration(task.start, task.end);
          const energyLevel = getEnergyLevel(task.start);
          const isHighlight = task.original_task.includes("HIGH");

          return (
            <View key={itemId} style={styles.timelineItem}>
              <View style={styles.timeColumn}>
                <Text style={styles.timeText}>
                  {hours}:{minutes}
                </Text>
                <Text style={styles.durationText}>{duration} min</Text>
              </View>

              <View style={styles.timelineLine}>
                <View
                  style={[
                    styles.timelineDot,
                    isCompleted && styles.timelineDotCompleted,
                    isHighlight && styles.timelineDotHighlight,
                  ]}
                />
                {index < filteredItems.length - 1 && (
                  <View style={styles.verticalLine} />
                )}
              </View>

              <View style={styles.cardContainer}>
                <View
                  style={[
                    styles.activityCard,
                    isCompleted && styles.activityCardCompleted,
                  ]}
                >
                  <Text style={styles.activityTitle}>
                    {task.original_task.replace(/\[HIGH\]|\[MEDIUM\]|\[LOW\]/g, "").trim()}
                  </Text>

                  <View style={styles.tagsRow}>
                    <View style={styles.tag}>
                      <Feather name="zap" size={12} color={colors.warning} />
                      <Text style={styles.tagText}>{energyLevel}</Text>
                    </View>
                    {isHighlight && (
                      <View style={[styles.tag, styles.tagHighlight]}>
                        <Text style={styles.tagTextHighlight}>HIGHLIGHT</Text>
                      </View>
                    )}
                  </View>

                  {task.segments?.map((segment, segIndex) => (
                    <View key={segIndex}>
                      {segment.type === "work" ? (
                        <Text style={styles.activityDescription}>
                          {segment.activity}
                        </Text>
                      ) : (
                        <View style={styles.breakSegment}>
                          <Feather name="coffee" size={14} color={colors.warning} />
                          <Text style={styles.breakText}>
                            {segment.duration_minutes} min break - {segment.activity}
                          </Text>
                        </View>
                      )}
                    </View>
                  ))}

                  <TouchableOpacity
                    style={[
                      styles.completeButton,
                      isCompleted && styles.completeButtonDone,
                    ]}
                    onPress={() => toggleComplete(itemId)}
                  >
                    <Feather
                      name={isCompleted ? "check-circle" : "circle"}
                      size={20}
                      color={isCompleted ? colors.success : colors.textMuted}
                    />
                    <Text
                      style={[
                        styles.completeButtonText,
                        isCompleted && styles.completeButtonTextDone,
                      ]}
                    >
                      {isCompleted ? "Completed" : "Tap to complete"}
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          );
        })}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <ActivityIndicator size="large" color={colors.accent} />
        <Text style={styles.loadingText}>Loading your day...</Text>
      </View>
    );
  }

  if (!timeline) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Feather name="calendar" size={48} color={colors.textMuted} />
        <Text style={styles.emptyText}>No schedule available</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={loadTimeline}>
          <Text style={styles.refreshButtonText}>Refresh</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const momentum = calculateMomentum();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Plan My Day</Text>
        <TouchableOpacity style={styles.profileButton}>
          <Feather name="user" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.accent}
          />
        }
      >
        <View style={styles.momentumCard}>
          <Text style={styles.momentumTitle}>Shape your flow</Text>
          <View style={styles.momentumContent}>
            <Text style={styles.momentumLabel}>DAILY MOMENTUM</Text>
            <Text style={styles.momentumValue}>{momentum}%</Text>
          </View>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${momentum}%` }]} />
          </View>
          <View style={styles.starsRow}>
            {[0, 1, 2].map((i) => (
              <Feather
                key={i}
                name="star"
                size={20}
                color={i < Math.floor(momentum / 33) ? colors.warning : colors.divider}
              />
            ))}
          </View>
        </View>

        {timeline.sections?.map((section, index) => {
          if (section.section_type === "focus_routine") {
            return renderFocusRoutine(section, index);
          } else if (section.section_type === "work_schedule") {
            return renderWorkSchedule(section, index);
          }
          return null;
        })}

        <View style={styles.footer} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1e2749",
  },
  centerContent: {
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl + 10,
    paddingBottom: spacing.lg,
    backgroundColor: "#1e2749",
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  profileButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "#2d3f6f",
    justifyContent: "center",
    alignItems: "center",
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  momentumCard: {
    backgroundColor: "#2d3f6f",
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  momentumTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  momentumContent: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  momentumLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.textMuted,
    letterSpacing: 1,
  },
  momentumValue: {
    fontSize: 32,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  progressBar: {
    height: 6,
    backgroundColor: "#1e2749",
    borderRadius: 3,
    marginBottom: spacing.md,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 3,
  },
  starsRow: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
    gap: spacing.sm,
  },
  sectionTitle: {
    fontSize: typography.heading3,
    fontWeight: "600",
    color: colors.accent,
  },
  timelineItem: {
    flexDirection: "row",
    marginBottom: spacing.md,
  },
  timeColumn: {
    width: 70,
    paddingTop: 4,
  },
  timeText: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  durationText: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
  },
  timelineLine: {
    width: 30,
    alignItems: "center",
    marginRight: spacing.md,
  },
  timelineDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.accent,
    borderWidth: 3,
    borderColor: "#1e2749",
  },
  timelineDotCompleted: {
    backgroundColor: colors.success,
  },
  timelineDotHighlight: {
    backgroundColor: colors.warning,
  },
  verticalLine: {
    width: 2,
    flex: 1,
    backgroundColor: "#3d4f7f",
    marginTop: 4,
  },
  cardContainer: {
    flex: 1,
  },
  activityCard: {
    backgroundColor: "#2d3f6f",
    borderRadius: radius.md,
    padding: spacing.md,
  },
  activityCardCompleted: {
    opacity: 0.6,
  },
  activityTitle: {
    fontSize: typography.heading3,
    fontWeight: "600",
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  tagsRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  tag: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(251, 191, 36, 0.15)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radius.sm,
  },
  tagMindful: {
    backgroundColor: "rgba(79, 70, 229, 0.15)",
  },
  tagHighlight: {
    backgroundColor: colors.accent,
  },
  tagText: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.textSecondary,
  },
  tagTextHighlight: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.textPrimary,
    letterSpacing: 0.5,
  },
  activityDescription: {
    fontSize: typography.body,
    color: colors.textSecondary,
    lineHeight: 21,
    marginBottom: spacing.md,
  },
  breakSegment: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.md,
    padding: spacing.sm,
    backgroundColor: "rgba(251, 191, 36, 0.1)",
    borderRadius: radius.sm,
  },
  breakText: {
    fontSize: typography.small,
    color: colors.textSecondary,
  },
  completeButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderColor: colors.divider,
  },
  completeButtonDone: {
    backgroundColor: "rgba(34, 197, 94, 0.15)",
    borderColor: colors.success,
  },
  completeButtonText: {
    fontSize: typography.body,
    fontWeight: "500",
    color: colors.textMuted,
  },
  completeButtonTextDone: {
    color: colors.success,
  },
  loadingText: {
    fontSize: typography.body,
    color: colors.textMuted,
    marginTop: spacing.md,
  },
  emptyText: {
    fontSize: typography.heading3,
    color: colors.textMuted,
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  refreshButton: {
    backgroundColor: colors.accent,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
  },
  refreshButtonText: {
    fontSize: typography.body,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  footer: {
    height: 40,
  },
});

