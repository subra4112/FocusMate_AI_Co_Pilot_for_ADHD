import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, typography, radius } from "../theme";

export function InsightCard({ title, metric, description }) {
  return (
    <View style={styles.card}>
      <Text style={styles.metric}>{metric}</Text>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    flexBasis: "48%",
    minWidth: "48%",
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  metric: {
    color: colors.accentSoft,
    fontSize: typography.heading3,
    fontWeight: "700",
  },
  title: {
    color: colors.textPrimary,
    fontSize: typography.body,
    marginTop: spacing.xs,
    fontWeight: "600",
  },
  description: {
    color: colors.textMuted,
    fontSize: typography.small,
    marginTop: spacing.sm,
    lineHeight: 18,
  },
});

