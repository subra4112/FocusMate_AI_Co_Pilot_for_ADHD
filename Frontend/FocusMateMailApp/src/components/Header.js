import { View, Text, Image, StyleSheet } from "react-native";
import { colors, spacing, typography, radius } from "../theme";

const avatarUri =
  "https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&w=200&q=80";

export function Header() {
  const date = new Date();
  const month = date.toLocaleString("default", { month: "long" });
  const day = date.getDate();

  return (
    <View style={styles.container}>
      <View>
        <Text style={styles.greeting}>FocusMate Mail</Text>
        <Text style={styles.dateLabel}>{`${month} ${day}`}</Text>
      </View>
      <Image source={{ uri: avatarUri }} style={styles.avatar} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  greeting: {
    color: colors.textPrimary,
    fontSize: typography.heading2,
    fontWeight: "700",
  },
  dateLabel: {
    marginTop: spacing.xs,
    color: colors.textMuted,
    fontSize: typography.body,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: radius.pill,
    borderWidth: 2,
    borderColor: colors.accentSoft,
  },
});

