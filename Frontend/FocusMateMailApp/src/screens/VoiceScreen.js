import { useEffect, useMemo, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Easing,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { Audio } from "expo-av";
import { Feather } from "@expo/vector-icons";
import { colors, spacing, radius, typography } from "../theme";
import { transcribeAudioAsync } from "../services/voice";

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

export function VoiceScreen() {
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState(null);
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  const [transcript, setTranscript] = useState("");
  const [tasks, setTasks] = useState([]);
  const [emotion, setEmotion] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Tap to capture a voice note");
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const pulse = useRef(new Animated.Value(1)).current;
  const waveOne = useRef(new Animated.Value(1)).current;
  const waveTwo = useRef(new Animated.Value(1)).current;
  const spinner = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (isRecording) {
      startAnimations();
    } else {
      stopAnimations();
    }
  }, [isRecording]);

  const startAnimations = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, {
          toValue: 1.08,
          duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulse, {
          toValue: 1,
          duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(waveOne, {
          toValue: 1.4,
          duration: 1400,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(waveOne, {
          toValue: 1,
          duration: 1400,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(waveTwo, {
          toValue: 1.6,
          duration: 1800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(waveTwo, {
          toValue: 1,
          duration: 1800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopAnimations = () => {
    pulse.stopAnimation(() => pulse.setValue(1));
    waveOne.stopAnimation(() => waveOne.setValue(1));
    waveTwo.stopAnimation(() => waveTwo.setValue(1));
  };

  useEffect(() => {
    Animated.loop(
      Animated.timing(spinner, {
        toValue: 1,
        duration: 2200,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();
  }, [spinner]);

  const rotation = useMemo(
    () =>
      spinner.interpolate({
        inputRange: [0, 1],
        outputRange: ["0deg", "360deg"],
      }),
    [spinner]
  );

  const handleToggleRecording = async () => {
    setErrorMessage("");

    if (isRecording) {
      await stopRecordingAsync();
    } else {
      await startRecordingAsync();
    }
  };

  const startRecordingAsync = async () => {
    try {
      if (!permissionResponse || permissionResponse.status !== "granted") {
        const result = await requestPermission();
        if (!result.granted) {
          setErrorMessage("Microphone permission is required.");
          return;
        }
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
      });

      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      setRecording(newRecording);
      setIsRecording(true);
      setStatusMessage("Listening… tap to stop");
      setTranscript("");
      setTasks([]);
      setEmotion(null);
    } catch (error) {
      console.error("Failed to start recording", error);
      setErrorMessage(error?.message || "Unable to start recording.");
      setIsRecording(false);
    }
  };

  const stopRecordingAsync = async () => {
    setIsRecording(false);
    setStatusMessage("Processing your voice note…");
    setIsProcessing(true);

    try {
      if (!recording) {
        setErrorMessage("No active recording found.");
        return;
      }

      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

      const uri = recording.getURI();
      setRecording(null);

      if (!uri) {
        setErrorMessage("Unable to access recorded audio.");
        return;
      }

      const result = await transcribeAudioAsync({ uri });
      const plainText = result?.text?.trim();
      const extractedTasks = Array.isArray(result?.tasks) ? result.tasks : [];

      if (plainText) {
        setTranscript(plainText);
        setStatusMessage("Captured note ready to review");
      } else {
        setTranscript("");
        setStatusMessage("No speech detected.");
      }

      setEmotion(result?.emotion || null);
      setTasks(extractedTasks);
    } catch (error) {
      console.error("Transcription failed", error);
      setErrorMessage(error?.message || "Unable to process audio.");
      setStatusMessage("Tap to capture a voice note");
    } finally {
      setIsProcessing(false);
    }
  };

  const activeTasks = tasks.filter((task) => task && task.action);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>FocusMate</Text>
          <Text style={styles.subtitle}>Capture tasks by speaking naturally.</Text>
        </View>
        <View style={styles.profileBadge}>
          <Feather name="user" size={24} color={colors.accent} />
        </View>
      </View>

      <View style={styles.recorderWrapper}>
        <Animated.View
          pointerEvents="none"
          style={[
            styles.wave,
            styles.waveOuter,
            { transform: [{ scale: isRecording ? waveTwo : 0 }] },
          ]}
        />
        <Animated.View
          pointerEvents="none"
          style={[
            styles.wave,
            styles.waveInner,
            { transform: [{ scale: isRecording ? waveOne : 0 }] },
          ]}
        />

        <Animated.View style={[styles.outerRing, { transform: [{ rotate: rotation }] }]}>
          <View style={styles.ringMarker} />
        </Animated.View>

        <AnimatedTouchable
          activeOpacity={0.8}
          style={[styles.micButton, { transform: [{ scale: pulse }] }]}
          onPress={handleToggleRecording}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator size="large" color={colors.accentSoft} />
          ) : (
            <Feather
              name={isRecording ? "mic" : "mic"}
              size={54}
              color={colors.accentSoft}
            />
          )}
        </AnimatedTouchable>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>{statusMessage}</Text>
        {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
      </View>

      {transcript ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Transcript</Text>
          <Text style={styles.sectionBody}>{transcript}</Text>
        </View>
      ) : null}

      {emotion ? (
        <View style={styles.emotionCard}>
          <Text style={styles.sectionTitle}>Detected Emotion</Text>
          <View style={styles.emotionRow}>
            <View style={styles.emotionPill}>
              <Feather name="activity" size={18} color={colors.accent} />
              <Text style={styles.emotionText}>{emotion?.primary}</Text>
            </View>
            <Text style={styles.emotionMeta}>{emotion?.valence}</Text>
            <Text style={styles.emotionMeta}>arousal: {emotion?.arousal}</Text>
          </View>
        </View>
      ) : null}

      {activeTasks.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tasks Identified</Text>
          <FlatList
            data={activeTasks}
            keyExtractor={(_, index) => String(index)}
            renderItem={({ item }) => (
              <View style={styles.taskChip}>
                <Feather name="check-circle" size={18} color={colors.accentSoft} />
                <View style={styles.taskContent}>
                  <Text style={styles.taskTitle}>{item.action}</Text>
                  {item?.due?.time || item?.due?.date ? (
                    <Text style={styles.taskMeta}>
                      {item?.due?.date ? item.due.date : ""}
                      {item?.due?.time ? ` • ${item.due.time}` : ""}
                    </Text>
                  ) : null}
                </View>
              </View>
            )}
            ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
          />
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.xl,
    gap: spacing.lg,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: {
    color: colors.textPrimary,
    fontSize: typography.heading1,
    fontWeight: "700",
  },
  subtitle: {
    color: colors.textMuted,
    fontSize: typography.body,
    marginTop: spacing.xs,
  },
  profileBadge: {
    width: 48,
    height: 48,
    borderRadius: radius.pill,
    backgroundColor: colors.card,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.divider,
  },
  recorderWrapper: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  micButton: {
    width: 200,
    height: 200,
    borderRadius: radius.pill,
    backgroundColor: colors.card,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: colors.accentSoft,
    shadowColor: colors.accent,
    shadowOpacity: 0.35,
    shadowRadius: 25,
    shadowOffset: { width: 0, height: 0 },
    elevation: 6,
  },
  wave: {
    position: "absolute",
    backgroundColor: colors.accent,
    opacity: 0.15,
    borderRadius: radius.pill,
  },
  waveInner: {
    width: 260,
    height: 260,
  },
  waveOuter: {
    width: 320,
    height: 320,
  },
  outerRing: {
    position: "absolute",
    width: 260,
    height: 260,
    borderRadius: radius.pill,
    borderWidth: 2,
    borderColor: colors.accentSoft,
    justifyContent: "center",
    alignItems: "center",
  },
  ringMarker: {
    position: "absolute",
    top: -2,
    width: 60,
    height: 4,
    borderRadius: radius.pill,
    backgroundColor: colors.accentSoft,
  },
  statusContainer: {
    alignItems: "center",
    marginTop: spacing.sm,
  },
  statusLabel: {
    color: colors.textSecondary,
    fontSize: typography.body,
  },
  errorText: {
    marginTop: spacing.xs,
    color: colors.danger,
    fontSize: typography.small,
  },
  section: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  sectionTitle: {
    color: colors.textPrimary,
    fontSize: typography.heading3,
    fontWeight: "600",
  },
  sectionBody: {
    color: colors.textSecondary,
    fontSize: typography.body,
    lineHeight: 22,
  },
  emotionCard: {
    backgroundColor: colors.cardSecondary,
    borderRadius: radius.lg,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  emotionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  emotionPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    backgroundColor: colors.chipBackground,
  },
  emotionText: {
    color: colors.accentSoft,
    fontSize: typography.small,
    textTransform: "capitalize",
  },
  emotionMeta: {
    color: colors.textMuted,
    fontSize: typography.small,
    textTransform: "capitalize",
  },
  taskChip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardSecondary,
    borderRadius: radius.lg,
    padding: spacing.md,
    gap: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  taskContent: {
    flex: 1,
  },
  taskTitle: {
    color: colors.textPrimary,
    fontSize: typography.body,
    fontWeight: "600",
  },
  taskMeta: {
    color: colors.textMuted,
    fontSize: typography.small,
    marginTop: spacing.xs,
  },
});
