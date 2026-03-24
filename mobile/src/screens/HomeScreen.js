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
import { ALCOHOL_HELP, QUICK_INPUTS, QUICK_LOGS } from "../utils/constants";

export default function HomeScreen({ navigation }) {
  const [input, setInput] = useState("");
  const [morningSugar, setMorningSugar] = useState("");
  const [bp, setBp] = useState("");
  const [water, setWater] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [foodWithDrink, setFoodWithDrink] = useState("");
  const [loading, setLoading] = useState(false);
  const {
    isAvailable,
    isListening,
    transcript,
    speechError,
    needsDevBuild,
    startListening,
    stopListening,
    clearTranscript,
  } = useSpeechToText();

  const combinedPreview = useMemo(
    () => buildCombinedEntry({ input, morningSugar, bp, water, symptoms, foodWithDrink }).trim(),
    [input, morningSugar, bp, water, symptoms, foodWithDrink]
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
    const combined = buildCombinedEntry({
      input: textValue,
      morningSugar,
      bp,
      water,
      symptoms,
      foodWithDrink,
    }).trim();

    if (!combined) {
      Alert.alert("Add details", "Enter the drink or food details and answer the quick questions first.");
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

  function appendQuickLog(text) {
    clearTranscript();
    setInput((current) => (current.trim() ? `${current.trim()}, ${text}` : text));
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
    <LinearGradient colors={["#09111F", "#13213C", "#1D2F54"]} style={styles.bg}>
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>PulseAI</Text>
          <Text style={styles.title}>Answer the basics first, then get one final answer.</Text>
          <Text style={styles.subtitle}>
            This works better when morning sugar, BP, water, and symptoms are asked before the final advice.
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

          <View style={styles.panelStrong}>
            <Text style={styles.panelTitle}>Quick health questions</Text>

            <Text style={styles.questionLabel}>What was the morning sugar?</Text>
            <TextInput
              keyboardType="numeric"
              onChangeText={setMorningSugar}
              placeholder="Example 150"
              placeholderTextColor="#94A3B8"
              style={styles.smallInput}
              value={morningSugar}
            />

            <Text style={styles.questionLabel}>What is the blood pressure right now?</Text>
            <TextInput
              onChangeText={setBp}
              placeholder="Example 150/95"
              placeholderTextColor="#94A3B8"
              style={styles.smallInput}
              value={bp}
            />

            <Text style={styles.questionLabel}>How much water was taken today?</Text>
            <TextInput
              onChangeText={setWater}
              placeholder="Example 500 ml or 2 glasses"
              placeholderTextColor="#94A3B8"
              style={styles.smallInput}
              value={water}
            />

            <Text style={styles.questionLabel}>What was eaten with the drink?</Text>
            <TextInput
              onChangeText={setFoodWithDrink}
              placeholder="Example chips or fried snacks"
              placeholderTextColor="#94A3B8"
              style={styles.smallInput}
              value={foodWithDrink}
            />

            <Text style={styles.questionLabel}>How are you feeling right now?</Text>
            <View style={styles.inlineButtons}>
              <Pressable onPress={() => setSymptoms("I am feeling normal")} style={styles.inlineButton}>
                <Text style={styles.inlineButtonText}>Normal</Text>
              </Pressable>
              <Pressable onPress={() => setSymptoms("feeling dizzy and weak")} style={styles.inlineButton}>
                <Text style={styles.inlineButtonText}>Dizzy/Weak</Text>
              </Pressable>
            </View>
            <TextInput
              multiline
              onChangeText={setSymptoms}
              placeholder="Type here. Example: I am feeling normal"
              placeholderTextColor="#94A3B8"
              style={styles.largeQuestionInput}
              textAlignVertical="top"
              value={symptoms}
            />
          </View>

          <View style={styles.panelStrong}>
            <Text style={styles.panelTitle}>Quick add</Text>
            <View style={styles.grid}>
              {QUICK_LOGS.map((item) => (
                <Pressable key={item.label} onPress={() => appendQuickLog(item.text)} style={styles.gridButton}>
                  <Text style={styles.gridButtonText}>{item.label}</Text>
                </Pressable>
              ))}
            </View>
          </View>

          <View style={styles.panel}>
            <Text style={styles.panelTitle}>Main entry</Text>
            <TextInput
              multiline
              onChangeText={setInput}
              placeholder="Example: 2 small pegs whiskey, chips"
              placeholderTextColor="#94A3B8"
              style={styles.input}
              value={input}
            />
            <Text style={styles.previewLabel}>What will be analyzed</Text>
            <Text style={styles.previewText}>{combinedPreview || "Nothing added yet."}</Text>
            <Pressable disabled={loading} onPress={() => handleAnalyze()} style={styles.primaryButton}>
              {loading ? <ActivityIndicator color="#FFF7ED" /> : <Text style={styles.primaryLabel}>Get final guidance</Text>}
            </Pressable>
          </View>

          <View style={styles.quickWrap}>
            <Text style={styles.sectionTitle}>Examples</Text>
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

function buildCombinedEntry({ input, morningSugar, bp, water, symptoms, foodWithDrink }) {
  const parts = [];
  if (input?.trim()) parts.push(input.trim());
  if (morningSugar?.trim()) parts.push(`morning sugar ${morningSugar.trim()}`);
  if (bp?.trim()) parts.push(`BP ${bp.trim()}`);
  if (water?.trim()) parts.push(water.toLowerCase().includes("water") ? water.trim() : `had ${water.trim()} water`);
  if (foodWithDrink?.trim()) parts.push(`ate ${foodWithDrink.trim()}`);
  if (symptoms?.trim()) parts.push(symptoms.trim());
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
    color: "#FDBA74",
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
  panelStrong: {
    backgroundColor: "rgba(251, 113, 133, 0.14)",
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
  questionLabel: {
    color: "#E2E8F0",
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 6,
    marginTop: 6,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  gridButton: {
    backgroundColor: "#1D3557",
    borderRadius: 16,
    minWidth: "47%",
    paddingHorizontal: 14,
    paddingVertical: 16,
  },
  gridButtonText: {
    color: "#EFF6FF",
    fontSize: 16,
    fontWeight: "700",
    textAlign: "center",
  },
  inlineButtons: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 10,
  },
  inlineButton: {
    backgroundColor: "#17304F",
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
  largeQuestionInput: {
    backgroundColor: "#0F172A",
    borderColor: "#475569",
    borderRadius: 16,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 16,
    marginBottom: 10,
    minHeight: 88,
    padding: 14,
  },
  previewLabel: {
    color: "#FDE68A",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 14,
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