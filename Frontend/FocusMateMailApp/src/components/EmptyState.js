import { View, Text, StyleSheet } from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, typography } from "../theme";

export function EmptyState({ message }) {
  return (
    <View style={styles.container}>
      <Feather name="inbox" size={48} color={colors.textMuted} />
      <Text style={styles.title}>Nothing here yet</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.xl,
    gap: spacing.sm,
  },
  title: {
    color: colors.textSecondary,
    fontSize: typography.body,
    fontWeight: "600",
  },
  message: {
    color: colors.textMuted,
    fontSize: typography.small,
    textAlign: "center",
    paddingHorizontal: spacing.lg,
    lineHeight: 18,
  },
});

