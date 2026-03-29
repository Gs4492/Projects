import { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";

import MicButton from "../components/MicButton";
import { analyzeText } from "../services/api";
import { useSpeechToText } from "../services/speech";
import { ALCOHOL_HELP, QUICK_INPUTS } from "../utils/constants";

export default function HomeScreen({ navigation }) {
  const [input, setInput] = useState("");
  const [bp, setBp] = useState("");
  const [sugar, setSugar] = useState("");
  const [feeling, setFeeling] = useState("");
  const [loading, setLoading] = useState(false);
  const {
    isAvailable,
    isListening,
    transcript,
    speechError,
    needsDevBuild,
    startListening,
    stopListening,
  } = useSpeechToText();

  const combinedPreview = useMemo(
    () => buildCombinedEntry({ input, bp, sugar, feeling }).trim(),
    [input, bp, sugar, feeling]
  );

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  useEffect(() => {
    if (speechError) {
      Alert.alert("Speech input issue", speechError);
    }
  }, [speechError]);

  async function handleAnalyze(textValue = input) {
    const combined = buildCombinedEntry({ input: textValue, bp, sugar, feeling }).trim();

    if (!combined) {
      Alert.alert("Add details", "Type or speak what was eaten, drunk, or measured first.");
      return;
    }

    try {
      setLoading(true);
      const result = await analyzeText(combined);
      navigation.navigate("Result", { result, inputText: combined });
    } catch (error) {
      Alert.alert(
        "Could not connect",
        "The phone could not reach the backend. Check internet or backend URL and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleMicPress() {
    if (!isAvailable && !isListening) {
      Alert.alert(
        "Speech setup needed",
        "Speech recognition needs a development build or APK. Expo Go can still preview the app UI."
      );
      return;
    }

    if (isListening) {
      stopListening();
      return;
    }

    await startListening();
  }

  return (
    <LinearGradient colors={["#07131F", "#10233B", "#16365C"]} style={styles.bg}>
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>PulseAI</Text>
          <Text style={styles.title}>Tell me what happened today.</Text>
          <Text style={styles.subtitle}>
            Food, alcohol, BP, sugar, water, and symptoms can all go in one simple note.
          </Text>

          <MicButton isListening={isListening} onPress={handleMicPress} transcript={transcript} />

          {needsDevBuild ? (
            <View style={styles.noticeBox}>
              <Text style={styles.noticeTitle}>Expo Go preview mode</Text>
              <Text style={styles.noticeText}>
                The app UI works here, but speech input needs a development build or APK.
              </Text>
            </View>
          ) : null}

          <View style={styles.mainPanel}>
            <Text style={styles.panelTitle}>What did you eat, drink, or measure?</Text>
            <Text style={styles.panelIntro}>
              Examples: rice and sweets, 2 small pegs whiskey, 1 large beer, BP 150/95, sugar 180, feeling weak.
            </Text>
            <TextInput
              multiline
              onChangeText={setInput}
              placeholder="Example: rice and sweets, or 2 small pegs whiskey and chips"
              placeholderTextColor="#94A3B8"
              style={styles.input}
              value={input}
            />
          </View>

          <View style={styles.panelStrong}>
            <Text style={styles.panelTitle}>Optional helpers</Text>
            <Text style={styles.helperText}>Use these only if it feels easier than typing everything in the main note.</Text>

            <View style={styles.helperRow}>
              <View style={styles.helperField}>
                <Text style={styles.questionLabel}>BP</Text>
                <TextInput
                  onChangeText={setBp}
                  placeholder="150/95"
                  placeholderTextColor="#94A3B8"
                  style={styles.smallInput}
                  value={bp}
                />
              </View>
              <View style={styles.helperField}>
                <Text style={styles.questionLabel}>Sugar</Text>
                <TextInput
                  onChangeText={setSugar}
                  placeholder="180"
                  placeholderTextColor="#94A3B8"
                  style={styles.smallInput}
                  value={sugar}
                />
              </View>
            </View>

            <Text style={styles.questionLabel}>Feeling</Text>
            <View style={styles.inlineButtons}>
              <Pressable onPress={() => setFeeling("I am feeling normal")} style={styles.inlineButton}>
                <Text style={styles.inlineButtonText}>Normal</Text>
              </Pressable>
              <Pressable onPress={() => setFeeling("feeling dizzy and weak")} style={styles.inlineButton}>
                <Text style={styles.inlineButtonText}>Dizzy/Weak</Text>
              </Pressable>
            </View>
            <TextInput
              onChangeText={setFeeling}
              placeholder="Example: I am feeling normal"
              placeholderTextColor="#94A3B8"
              style={styles.smallInput}
              value={feeling}
            />
          </View>

          <View style={styles.panel}>
            <Text style={styles.previewLabel}>What will be analyzed</Text>
            <Text style={styles.previewText}>{combinedPreview || "Nothing added yet."}</Text>
            <Pressable disabled={loading} onPress={() => handleAnalyze()} style={styles.primaryButton}>
              {loading ? <ActivityIndicator color="#FFF7ED" /> : <Text style={styles.primaryLabel}>Get guidance</Text>}
            </Pressable>
          </View>

          <View style={styles.quickWrap}>
            <Text style={styles.sectionTitle}>Try these examples</Text>
            {QUICK_INPUTS.map((item) => (
              <Pressable key={item} onPress={() => setInput(item)} style={styles.quickChip}>
                <Text style={styles.quickChipText}>{item}</Text>
              </Pressable>
            ))}
          </View>

          <View style={styles.panel}>
            <Text style={styles.panelTitle}>Alcohol size guide</Text>
            {ALCOHOL_HELP.map((item) => (
              <Text key={item} style={styles.helpText}>
                {item}
              </Text>
            ))}
            <Text style={styles.disclaimer}>
              Guidance only. This app is not a doctor or emergency service.
            </Text>
          </View>

          <Pressable onPress={() => navigation.navigate("History")} style={styles.secondaryButton}>
            <Text style={styles.secondaryLabel}>View history</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

function buildCombinedEntry({ input, bp, sugar, feeling }) {
  const parts = [];
  if (input?.trim()) parts.push(input.trim());
  if (bp?.trim()) parts.push(`BP ${bp.trim()}`);
  if (sugar?.trim()) parts.push(`sugar ${sugar.trim()}`);
  if (feeling?.trim()) parts.push(feeling.trim());
  return parts.join(", ");
}

const styles = StyleSheet.create({
  bg: { flex: 1 },
  safe: { flex: 1 },
  content: {
    padding: 20,
    paddingBottom: 36,
  },
  eyebrow: {
    color: "#FBBF24",
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 1.6,
    marginBottom: 10,
    textTransform: "uppercase",
  },
  title: {
    color: "#F8FAFC",
    fontSize: 34,
    fontWeight: "900",
    lineHeight: 40,
    marginBottom: 10,
  },
  subtitle: {
    color: "#D6E3F3",
    fontSize: 18,
    lineHeight: 26,
    marginBottom: 24,
  },
  noticeBox: {
    backgroundColor: "rgba(250, 204, 21, 0.14)",
    borderRadius: 20,
    marginTop: 16,
    padding: 16,
  },
  noticeTitle: {
    color: "#FDE68A",
    fontSize: 18,
    fontWeight: "800",
    marginBottom: 6,
  },
  noticeText: {
    color: "#FEF3C7",
    fontSize: 15,
    lineHeight: 22,
  },
  mainPanel: {
    backgroundColor: "rgba(15, 23, 42, 0.78)",
    borderRadius: 24,
    marginTop: 20,
    padding: 18,
  },
  panelStrong: {
    backgroundColor: "rgba(59, 130, 246, 0.14)",
    borderRadius: 24,
    marginTop: 20,
    padding: 18,
  },
  panel: {
    backgroundColor: "rgba(15, 23, 42, 0.78)",
    borderRadius: 24,
    marginTop: 20,
    padding: 18,
  },
  panelTitle: {
    color: "#F8FAFC",
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 14,
  },
  panelIntro: {
    color: "#CBD5E1",
    fontSize: 16,
    lineHeight: 23,
    marginBottom: 12,
  },
  helperText: {
    color: "#D6E3F3",
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 12,
  },
  questionLabel: {
    color: "#E2E8F0",
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 6,
  },
  helperRow: {
    flexDirection: "row",
    gap: 12,
  },
  helperField: {
    flex: 1,
  },
  inlineButtons: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 10,
  },
  inlineButton: {
    backgroundColor: "#123356",
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  inlineButtonText: {
    color: "#E0F2FE",
    fontSize: 14,
    fontWeight: "700",
  },
  input: {
    backgroundColor: "#0F172A",
    borderColor: "#475569",
    borderRadius: 18,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 18,
    minHeight: 120,
    padding: 18,
    textAlignVertical: "top",
  },
  smallInput: {
    backgroundColor: "#0F172A",
    borderColor: "#475569",
    borderRadius: 16,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 16,
    marginBottom: 10,
    padding: 14,
  },
  previewLabel: {
    color: "#FDE68A",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 6,
    textTransform: "uppercase",
  },
  previewText: {
    color: "#E2E8F0",
    fontSize: 17,
    lineHeight: 24,
  },
  primaryButton: {
    alignItems: "center",
    backgroundColor: "#F97316",
    borderRadius: 18,
    marginTop: 16,
    paddingVertical: 18,
  },
  primaryLabel: {
    color: "#FFF7ED",
    fontSize: 22,
    fontWeight: "900",
  },
  quickWrap: {
    marginTop: 22,
  },
  sectionTitle: {
    color: "#E2E8F0",
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 12,
  },
  quickChip: {
    backgroundColor: "#172554",
    borderRadius: 18,
    marginBottom: 10,
    padding: 16,
  },
  quickChipText: {
    color: "#DBEAFE",
    fontSize: 16,
    lineHeight: 23,
  },
  helpText: {
    color: "#E2E8F0",
    fontSize: 16,
    marginBottom: 10,
  },
  disclaimer: {
    color: "#FCA5A5",
    fontSize: 14,
    lineHeight: 20,
    marginTop: 10,
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: "#94A3B8",
    borderRadius: 18,
    borderWidth: 1,
    marginTop: 20,
    paddingVertical: 16,
  },
  secondaryLabel: {
    color: "#E2E8F0",
    fontSize: 18,
    fontWeight: "800",
  },
});
