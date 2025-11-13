import { Pressable, Text, View, StyleSheet } from "react-native";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, typography, radius } from "../theme";

export function QuickActionButton({ icon, label, description, onPress }) {
  return (
    <Pressable style={styles.button} onPress={onPress}>
      <View style={styles.iconChip}>
        <Feather name={icon} size={18} color={colors.accentSoft} />
      </View>
      <View style={styles.textGroup}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.description}>{description}</Text>
      </View>
      <Feather name="chevron-right" size={18} color={colors.textMuted} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: colors.cardSecondary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.divider,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  iconChip: {
    width: 36,
    height: 36,
    borderRadius: radius.pill,
    backgroundColor: colors.chipBackground,
    alignItems: "center",
    justifyContent: "center",
  },
  textGroup: {
    flex: 1,
  },
  label: {
    color: colors.textPrimary,
    fontSize: typography.body,
    fontWeight: "600",
  },
  description: {
    color: colors.textMuted,
    marginTop: spacing.xs,
    fontSize: typography.small,
  },
});

