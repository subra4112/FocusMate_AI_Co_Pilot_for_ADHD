import { Pressable, Text, View, StyleSheet } from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, typography, radius } from "../theme";
import { formatRelativeTimestamp, formatDueLabel } from "../utils/dates";

const classificationConfig = {
  task: { label: "Task", color: colors.accentSoft, icon: "check-circle" },
  instruction: { label: "Instruction", color: colors.success, icon: "list" },
  article: { label: "Article", color: colors.warning, icon: "book" },
};

export function EmailCard({ email, onPress }) {
  const config = classificationConfig[email.classification] || classificationConfig.article;
  const timestamp = formatRelativeTimestamp(email.receivedAt);
  const dueLabel = formatDueLabel(email.due);
  const priorityLabel = email.priorityBucket ? `${email.priorityBucket} priority` : null;
  const notePreview = email.notes?.[0];

  return (
    <Pressable style={styles.card} onPress={() => onPress(email)}>
      <View style={styles.headerRow}>
        <View style={styles.classificationChip}>
          <Feather name={config.icon} size={14} color={config.color} />
          <Text style={[styles.classificationLabel, { color: config.color }]}>
            {config.label}
          </Text>
        </View>
        <Text style={styles.timestamp}>{timestamp}</Text>
      </View>

      <Text style={styles.subject} numberOfLines={2}>
        {email.subject}
      </Text>
      <Text style={styles.sender}>{email.sender}</Text>

      {priorityLabel ? (
        <View style={styles.priorityRow}>
          <Feather name="flag" size={12} color={colors.accentSoft} />
          <Text style={styles.priorityLabel}>{priorityLabel}</Text>
        </View>
      ) : null}

      {email.summary ? (
        <Text style={styles.summary} numberOfLines={3}>
          {email.summary}
        </Text>
      ) : null}

      {notePreview ? (
        <View style={styles.notePreview}>
          <Feather name="corner-down-right" size={12} color={colors.textMuted} />
          <Text style={styles.noteText} numberOfLines={2}>
            {notePreview}
          </Text>
        </View>
      ) : null}

      {dueLabel ? (
        <View style={styles.dueChip}>
          <Feather name="clock" size={12} color={colors.textPrimary} />
          <Text style={styles.dueLabel}>{dueLabel}</Text>
        </View>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
    gap: spacing.sm,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  classificationChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    backgroundColor: colors.chipBackground,
    borderRadius: radius.pill,
  },
  classificationLabel: {
    fontSize: typography.small,
    fontWeight: "600",
  },
  timestamp: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
  subject: {
    color: colors.textPrimary,
    fontSize: typography.heading3,
    fontWeight: "700",
  },
  sender: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
  priorityRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  priorityLabel: {
    color: colors.textMuted,
    fontSize: typography.small,
    fontWeight: "600",
  },
  summary: {
    color: colors.textSecondary,
    fontSize: typography.body,
    lineHeight: 20,
  },
  notePreview: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.xs,
  },
  noteText: {
    flex: 1,
    color: colors.textMuted,
    fontSize: typography.small,
    lineHeight: 18,
  },
  dueChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.accent,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
  },
  dueLabel: {
    color: colors.textPrimary,
    fontSize: typography.micro,
    fontWeight: "600",
  },
});

