import { View, Pressable, Text, StyleSheet } from "react-native";
import { colors, spacing, typography, radius } from "../theme";

const categories = [
  { id: "all", label: "All" },
  { id: "task", label: "Tasks" },
  { id: "instruction", label: "Instructions" },
  { id: "article", label: "Articles" },
];

export function CategoryFilter({ selected, onSelect }) {
  return (
    <View style={styles.container}>
      {categories.map((category) => {
        const isActive = selected === category.id;
        return (
          <Pressable
            key={category.id}
            style={[styles.chip, isActive && styles.chipActive]}
            onPress={() => onSelect(category.id)}
          >
            <Text style={[styles.chipLabel, isActive && styles.chipLabelActive]}>
              {category.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.chipBackground,
  },
  chipActive: {
    backgroundColor: colors.chipSelected,
    borderWidth: 1,
    borderColor: colors.accent,
  },
  chipLabel: {
    color: colors.textSecondary,
    fontSize: typography.small,
    fontWeight: "600",
  },
  chipLabelActive: {
    color: colors.textPrimary,
  },
});

