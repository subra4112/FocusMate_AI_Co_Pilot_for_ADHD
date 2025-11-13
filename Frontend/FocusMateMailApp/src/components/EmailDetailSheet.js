import {
  Modal,
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  SafeAreaView,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, typography, radius } from "../theme";
import { formatRelativeTimestamp, formatDueLabel } from "../utils/dates";

const classificationLabels = {
  task: "Task",
  instruction: "Instruction",
  article: "Article",
};

export function EmailDetailSheet({ email, visible, onClose }) {
  if (!email) {
    return null;
  }

  const timestamp = formatRelativeTimestamp(email.receivedAt);
  const dueLabel = formatDueLabel(email.due);
  const classificationLabel =
    classificationLabels[email.classification] || classificationLabels.article;

  return (
    <Modal visible={visible} animationType="slide" statusBarTranslucent>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <Pressable style={styles.backButton} onPress={onClose} hitSlop={12}>
            <Feather name="chevron-left" size={20} color={colors.textPrimary} />
            <Text style={styles.backLabel}>Back</Text>
          </Pressable>
        </View>

        <ScrollView
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.subject}>{email.subject}</Text>
          <Text style={styles.meta}>{`${email.sender} • ${timestamp}`}</Text>

          <View style={styles.metaRow}>
            <View style={styles.metaChip}>
              <Feather name="layers" size={14} color={colors.textPrimary} />
              <Text style={styles.metaChipLabel}>{classificationLabel}</Text>
            </View>
            {email.priorityBucket ? (
              <View style={styles.metaChip}>
                <Feather name="flag" size={14} color={colors.textPrimary} />
                <Text style={styles.metaChipLabel}>
                  {`${email.priorityBucket} priority`}
                </Text>
              </View>
            ) : null}
          </View>

          {dueLabel ? (
            <View style={styles.dueBanner}>
              <Feather name="calendar" size={16} color={colors.textPrimary} />
              <Text style={styles.dueBannerText}>{dueLabel}</Text>
            </View>
          ) : null}

          {email.summary ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Summary</Text>
              <Text style={styles.sectionBody}>{email.summary}</Text>
            </View>
          ) : null}

          {email.priorityReasoning ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Why it matters</Text>
              <Text style={styles.sectionBody}>{email.priorityReasoning}</Text>
            </View>
          ) : null}

          {email.steps && email.steps.length ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Suggested Steps</Text>
              <View style={styles.steps}>
                {email.steps.map((step, index) => (
                  <View key={step} style={styles.stepRow}>
                    <View style={styles.stepBadge}>
                      <Text style={styles.stepIndex}>{index + 1}</Text>
                    </View>
                    <Text style={styles.stepText}>{step}</Text>
                  </View>
                ))}
              </View>
            </View>
          ) : null}

          {email.notes && email.notes.length ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Notes</Text>
              <View style={styles.notes}>
                {email.notes.map((note) => (
                  <View key={note} style={styles.noteCard}>
                    <Feather
                      name="corner-down-right"
                      size={16}
                      color={colors.accentSoft}
                    />
                    <Text style={styles.noteText}>{note}</Text>
                  </View>
                ))}
              </View>
            </View>
          ) : null}
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.cardSecondary,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  backLabel: {
    color: colors.textPrimary,
    fontSize: typography.small,
    fontWeight: "600",
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
    paddingTop: spacing.sm,
    paddingBottom: spacing.xl,
    gap: spacing.lg,
  },
  subject: {
    color: colors.textPrimary,
    fontSize: typography.heading2,
    fontWeight: "700",
  },
  meta: {
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
  metaRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  metaChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.cardSecondary,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  metaChipLabel: {
    color: colors.textSecondary,
    fontSize: typography.small,
    fontWeight: "600",
  },
  section: {
    gap: spacing.sm,
  },
  sectionTitle: {
    color: colors.textSecondary,
    fontSize: typography.body,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 1.1,
  },
  sectionBody: {
    color: colors.textPrimary,
    fontSize: typography.body,
    lineHeight: 21,
  },
  steps: {
    gap: spacing.sm,
  },
  stepRow: {
    flexDirection: "row",
    gap: spacing.md,
    alignItems: "flex-start",
  },
  stepBadge: {
    width: 28,
    height: 28,
    borderRadius: radius.pill,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  stepIndex: {
    color: colors.textPrimary,
    fontWeight: "700",
  },
  stepText: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: typography.body,
    lineHeight: 21,
  },
  notes: {
    gap: spacing.sm,
  },
  noteCard: {
    flexDirection: "row",
    gap: spacing.md,
    backgroundColor: colors.cardSecondary,
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  noteText: {
    flex: 1,
    color: colors.textSecondary,
    fontSize: typography.body,
    lineHeight: 21,
  },
  dueBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.cardSecondary,
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.accentSoft,
  },
  dueBannerText: {
    color: colors.textPrimary,
    fontWeight: "600",
    fontSize: typography.body,
  },
});

