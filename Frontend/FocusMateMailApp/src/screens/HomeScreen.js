import { useCallback, useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, FlatList, ActivityIndicator, Alert } from "react-native";
import { StatusBar } from "expo-status-bar";
import { colors, spacing, typography, radius } from "../theme";
import { Header } from "../components/Header";
import { CategoryFilter } from "../components/CategoryFilter";
import { EmailCard } from "../components/EmailCard";
import { EmptyState } from "../components/EmptyState";
import { EmailDetailSheet } from "../components/EmailDetailSheet";
import { fetchEmails } from "../services/emails";

const keyExtractor = (item) => item.id;

export function HomeScreen() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [sheetVisible, setSheetVisible] = useState(false);
  const [emailsByCategory, setEmailsByCategory] = useState({
    task: [],
    instruction: [],
    article: [],
  });
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadEmails = useCallback(
    async ({ showLoader = true, categoryOverride } = {}) => {
      if (showLoader) {
        setLoading(true);
      }
      setErrorMessage("");
      try {
        const data = await fetchEmails({
          category: categoryOverride || selectedCategory,
          limit: 6,
        });
        setEmailsByCategory(data);
        setLastUpdated(new Date());
      } catch (err) {
        console.error("Failed to load emails:", err);
        const readable = err?.message || "Unable to load inbox.";
        setErrorMessage(readable);
        Alert.alert("Fetch failed", readable);
      } finally {
        if (showLoader) {
          setLoading(false);
        }
        setRefreshing(false);
      }
    },
    [selectedCategory]
  );

  useEffect(() => {
    loadEmails({ showLoader: true });
  }, [loadEmails]);

  const filteredEmails = useMemo(() => {
    const { task, instruction, article } = emailsByCategory;
    if (selectedCategory === "all") {
      return [...task, ...instruction, ...article].sort((a, b) => {
        const aDate = a.receivedAt ? new Date(a.receivedAt).getTime() : 0;
        const bDate = b.receivedAt ? new Date(b.receivedAt).getTime() : 0;
        return bDate - aDate;
      });
    }
    return emailsByCategory[selectedCategory] || [];
  }, [emailsByCategory, selectedCategory]);

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    loadEmails({ showLoader: false, categoryOverride: category });
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadEmails({ showLoader: false });
  };

  const lastUpdatedLabel = lastUpdated
    ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : null;

  const showEmptyState = !loading && filteredEmails.length === 0;

  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
    setSheetVisible(true);
  };

  const handleCloseSheet = () => {
    setSheetVisible(false);
    setSelectedEmail(null);
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <FlatList
        data={filteredEmails}
        keyExtractor={keyExtractor}
        ListHeaderComponent={
          <View style={styles.headerContent}>
            <Header />
            <Text style={styles.subtitle}>
              Triage, capture, and follow through with ADHD-friendly nudges.
            </Text>

            <CategoryFilter
              selected={selectedCategory}
              onSelect={handleCategoryChange}
            />

            {lastUpdatedLabel ? (
              <Text style={styles.updatedLabel}>{lastUpdatedLabel}</Text>
            ) : null}

            {errorMessage ? (
              <View style={styles.errorBanner}>
                <Text style={styles.errorText}>{errorMessage}</Text>
              </View>
            ) : null}

            <Text style={styles.sectionSubtitle}>
              Focus on the next best email to unblock future you.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <EmailCard email={item} onPress={handleSelectEmail} />
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          showEmptyState ? (
            <EmptyState message="No emails match this filter — try syncing again or pick a different category." />
          ) : null
        }
        showsVerticalScrollIndicator={false}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        ListFooterComponent={
          loading ? (
            <View style={styles.loadingState}>
              <ActivityIndicator color={colors.accentSoft} />
              <Text style={styles.loadingLabel}>Fetching latest inbox…</Text>
            </View>
          ) : null
        }
      />
      <EmailDetailSheet
        email={selectedEmail}
        visible={sheetVisible}
        onClose={handleCloseSheet}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
    gap: spacing.md,
  },
  headerContent: {
    gap: spacing.lg,
    marginBottom: spacing.lg,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: typography.body,
    lineHeight: 22,
  },
  updatedLabel: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
  errorBanner: {
    backgroundColor: "rgba(249, 115, 22, 0.12)",
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.danger,
  },
  errorText: {
    color: colors.danger,
    fontSize: typography.small,
  },
  sectionHeader: {
    gap: spacing.sm,
  },
  sectionTitle: {
    color: colors.textPrimary,
    fontSize: typography.heading3,
    fontWeight: "700",
  },
  sectionSubtitle: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
  actionsStack: {
    gap: spacing.sm,
  },
  separator: {
    height: spacing.md,
  },
  loadingState: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.lg,
    gap: spacing.sm,
  },
  loadingLabel: {
    color: colors.textMuted,
    fontSize: typography.small,
  },
});

