import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, radius, typography } from "../theme";

export const TimelineCard = ({
  time,
  duration,
  title,
  description,
  tags,
  isCompleted,
  onToggleComplete,
  isHighlight = false,
}) => {
  const { hours, minutes } = parseTime(time);

  return (
    <View style={styles.container}>
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
        <View style={styles.verticalLine} />
      </View>

      <View style={styles.cardContainer}>
        <View
          style={[
            styles.card,
            isCompleted && styles.cardCompleted,
          ]}
        >
          <Text style={styles.title}>{title}</Text>

          {tags && tags.length > 0 && (
            <View style={styles.tagsRow}>
              {tags.map((tag, index) => (
                <View
                  key={index}
                  style={[
                    styles.tag,
                    tag.type === "highlight" && styles.tagHighlight,
                    tag.type === "mindful" && styles.tagMindful,
                  ]}
                >
                  {tag.icon && (
                    <Feather
                      name={tag.icon}
                      size={12}
                      color={tag.type === "highlight" ? colors.textPrimary : tag.color}
                    />
                  )}
                  <Text
                    style={[
                      styles.tagText,
                      tag.type === "highlight" && styles.tagTextHighlight,
                    ]}
                  >
                    {tag.label}
                  </Text>
                </View>
              ))}
            </View>
          )}

          {description && (
            <Text style={styles.description}>{description}</Text>
          )}

          <TouchableOpacity
            style={[
              styles.completeButton,
              isCompleted && styles.completeButtonDone,
            ]}
            onPress={onToggleComplete}
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

const styles = StyleSheet.create({
  container: {
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
  card: {
    backgroundColor: "#2d3f6f",
    borderRadius: radius.md,
    padding: spacing.md,
  },
  cardCompleted: {
    opacity: 0.6,
  },
  title: {
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
  description: {
    fontSize: typography.body,
    color: colors.textSecondary,
    lineHeight: 21,
    marginBottom: spacing.md,
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
});


