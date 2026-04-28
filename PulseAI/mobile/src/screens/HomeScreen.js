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
import { ALCOHOL_HELP, LANDING_SECTIONS } from "../utils/constants";

export default function HomeScreen({ navigation }) {
  const [food, setFood] = useState("");
  const [drinks, setDrinks] = useState("");
  const [bp, setBp] = useState("");
  const [sugar, setSugar] = useState("");
  const [water, setWater] = useState("");
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
    () => buildCombinedEntry({ food, drinks, bp, sugar, water, feeling }).trim(),
    [food, drinks, bp, sugar, water, feeling]
  );

  useEffect(() => {
    if (transcript) {
      setFood((current) => current || transcript);
    }
  }, [transcript]);

  useEffect(() => {
    if (speechError) {
      Alert.alert("Speech input issue", speechError);
    }
  }, [speechError]);

  async function handleAnalyze() {
    const combined = buildCombinedEntry({ food, drinks, bp, sugar, water, feeling }).trim();

    if (!combined) {
      Alert.alert("Add details", "Fill at least one section before getting guidance.");
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
    <LinearGradient colors={["#07101E", "#0B1B2D", "#0F3556"]} style={styles.bg}>
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.hero}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>PulseAI</Text>
            </View>
            <Text style={styles.title}>Log each part separately so the guidance feels clearer.</Text>
            <Text style={styles.subtitle}>
              Add food, drinks, readings, and how you feel in their own sections. The app combines them into one health check behind the scenes.
            </Text>
            <View style={styles.heroGrid}>
              {LANDING_SECTIONS.map((item) => (
                <View key={item.title} style={styles.heroCard}>
                  <Text style={styles.heroCardTitle}>{item.title}</Text>
                  <Text style={styles.heroCardBody}>{item.body}</Text>
                </View>
              ))}
            </View>
          </View>

          <MicButton isListening={isListening} onPress={handleMicPress} transcript={transcript} />

          {needsDevBuild ? (
            <View style={styles.noticeBox}>
              <Text style={styles.noticeTitle}>Preview mode</Text>
              <Text style={styles.noticeText}>
                The layout works here, but real speech input needs a development build or APK.
              </Text>
            </View>
          ) : null}

          <SectionCard eyebrow="Food" title="What food was eaten today?" tone="slate">
            <Text style={styles.sectionBody}>Examples: dal and rice, chips, sweets, burger and fries, fruit, normal home food.</Text>
            <TextInput
              multiline
              onChangeText={setFood}
              placeholder="Example: dal, rice, chips, and fruit"
              placeholderTextColor="#94A3B8"
              style={styles.input}
              value={food}
            />
          </SectionCard>

          <SectionCard eyebrow="Drinks" title="What drinks were taken?" tone="orange">
            <Text style={styles.sectionBody}>Add alcohol, water, tea, coffee, juice, or anything else taken during the day.</Text>
            <TextInput
              multiline
              onChangeText={setDrinks}
              placeholder="Example: 1 small peg whiskey, 2 glasses water"
              placeholderTextColor="#94A3B8"
              style={styles.input}
              value={drinks}
            />
            <View style={styles.inlineGuide}>
              {ALCOHOL_HELP.map((item) => (
                <View key={item} style={styles.inlineGuidePill}>
                  <Text style={styles.inlineGuideText}>{item}</Text>
                </View>
              ))}
            </View>
          </SectionCard>

          <SectionCard eyebrow="Health" title="Add readings if you have them" tone="green">
            <View style={styles.metricGrid}>
              <MetricField label="BP" placeholder="Example 150/95" value={bp} onChangeText={setBp} />
              <MetricField label="Sugar" placeholder="Example 180" value={sugar} onChangeText={setSugar} />
            </View>
            <MetricField
              label="Water"
              placeholder="Example 2 glasses or 500 ml"
              value={water}
              onChangeText={setWater}
            />
          </SectionCard>

          <SectionCard eyebrow="Feeling" title="How do you feel right now?" tone="blue">
            <Text style={styles.sectionBody}>Write something simple like: I am feeling normal, dizzy, weak, heavy, tired, or headache.</Text>
            <TextInput
              onChangeText={setFeeling}
              placeholder="Example: I am feeling normal"
              placeholderTextColor="#94A3B8"
              style={styles.singleInput}
              value={feeling}
            />
          </SectionCard>

          <View style={styles.previewCard}>
            <View style={styles.previewHeader}>
              <View>
                <Text style={styles.sectionEyebrow}>Preview</Text>
                <Text style={styles.sectionTitle}>What will be analyzed</Text>
              </View>
              <Pressable onPress={() => navigation.navigate("History")} style={styles.ghostButton}>
                <Text style={styles.ghostButtonText}>History</Text>
              </Pressable>
            </View>
            <Text style={styles.previewText}>{combinedPreview || "Your food, drinks, readings, and feeling will be combined here before analysis."}</Text>
            <Pressable disabled={loading} onPress={handleAnalyze} style={styles.primaryButton}>
              {loading ? <ActivityIndicator color="#FFF7ED" /> : <Text style={styles.primaryLabel}>Get guidance</Text>}
            </Pressable>
          </View>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

function SectionCard({ eyebrow, title, tone, children }) {
  return (
    <View style={[styles.sectionCard, tone === "orange" && styles.orangeCard, tone === "green" && styles.greenCard, tone === "blue" && styles.blueCard]}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionEyebrow}>{eyebrow}</Text>
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      {children}
    </View>
  );
}

function MetricField({ label, placeholder, value, onChangeText }) {
  return (
    <View style={styles.metricField}>
      <Text style={styles.metricLabel}>{label}</Text>
      <TextInput
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="#94A3B8"
        style={styles.metricInput}
        value={value}
      />
    </View>
  );
}

function buildCombinedEntry({ food, drinks, bp, sugar, water, feeling }) {
  const parts = [];
  if (food?.trim()) parts.push(`Food: ${food.trim()}`);
  if (drinks?.trim()) parts.push(`Drinks: ${drinks.trim()}`);
  if (bp?.trim()) parts.push(`BP: ${bp.trim()}`);
  if (sugar?.trim()) parts.push(`Sugar: ${sugar.trim()}`);
  if (water?.trim()) parts.push(`Water: ${water.trim()}`);
  if (feeling?.trim()) parts.push(`Feeling: ${feeling.trim()}`);
  return parts.join(" | ");
}

const styles = StyleSheet.create({
  bg: { flex: 1 },
  safe: { flex: 1 },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  hero: {
    marginBottom: 18,
  },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "rgba(251, 191, 36, 0.14)",
    borderRadius: 999,
    marginBottom: 14,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  badgeText: {
    color: "#FCD34D",
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 1.2,
    textTransform: "uppercase",
  },
  title: {
    color: "#F8FAFC",
    fontSize: 34,
    fontWeight: "900",
    letterSpacing: -0.6,
    lineHeight: 40,
    marginBottom: 12,
  },
  subtitle: {
    color: "#D6E3F3",
    fontSize: 17,
    lineHeight: 26,
    marginBottom: 18,
  },
  heroGrid: {
    gap: 12,
  },
  heroCard: {
    backgroundColor: "rgba(255,255,255,0.06)",
    borderColor: "rgba(255,255,255,0.08)",
    borderRadius: 22,
    borderWidth: 1,
    padding: 16,
  },
  heroCardTitle: {
    color: "#F8FAFC",
    fontSize: 18,
    fontWeight: "800",
    marginBottom: 6,
  },
  heroCardBody: {
    color: "#CBD5E1",
    fontSize: 15,
    lineHeight: 22,
  },
  noticeBox: {
    backgroundColor: "rgba(250, 204, 21, 0.14)",
    borderRadius: 22,
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
  sectionCard: {
    backgroundColor: "rgba(15, 23, 42, 0.78)",
    borderRadius: 28,
    marginTop: 18,
    padding: 20,
  },
  orangeCard: {
    backgroundColor: "rgba(249, 115, 22, 0.12)",
  },
  greenCard: {
    backgroundColor: "rgba(34, 197, 94, 0.12)",
  },
  blueCard: {
    backgroundColor: "rgba(59, 130, 246, 0.14)",
  },
  sectionHeader: {
    marginBottom: 12,
  },
  sectionEyebrow: {
    color: "#93C5FD",
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 1.1,
    marginBottom: 6,
    textTransform: "uppercase",
  },
  sectionTitle: {
    color: "#F8FAFC",
    fontSize: 24,
    fontWeight: "900",
    lineHeight: 30,
  },
  sectionBody: {
    color: "#CBD5E1",
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 14,
  },
  input: {
    backgroundColor: "#0F172A",
    borderColor: "rgba(148, 163, 184, 0.42)",
    borderRadius: 22,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 18,
    minHeight: 118,
    padding: 18,
    textAlignVertical: "top",
  },
  singleInput: {
    backgroundColor: "rgba(15, 23, 42, 0.9)",
    borderColor: "rgba(148, 163, 184, 0.42)",
    borderRadius: 18,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 16,
    padding: 14,
  },
  metricGrid: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 12,
  },
  metricField: {
    flex: 1,
  },
  metricLabel: {
    color: "#DCFCE7",
    fontSize: 15,
    fontWeight: "800",
    marginBottom: 6,
  },
  metricInput: {
    backgroundColor: "rgba(15, 23, 42, 0.9)",
    borderColor: "rgba(148, 163, 184, 0.42)",
    borderRadius: 18,
    borderWidth: 1,
    color: "#F8FAFC",
    fontSize: 16,
    padding: 14,
  },
  inlineGuide: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginTop: 14,
  },
  inlineGuidePill: {
    backgroundColor: "rgba(15, 23, 42, 0.84)",
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  inlineGuideText: {
    color: "#E2E8F0",
    fontSize: 14,
    fontWeight: "700",
  },
  previewCard: {
    backgroundColor: "rgba(15, 23, 42, 0.88)",
    borderRadius: 28,
    marginTop: 18,
    padding: 20,
  },
  previewHeader: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  previewText: {
    color: "#FFF7ED",
    fontSize: 17,
    lineHeight: 25,
    marginBottom: 16,
  },
  primaryButton: {
    alignItems: "center",
    backgroundColor: "#F97316",
    borderRadius: 18,
    paddingVertical: 18,
  },
  primaryLabel: {
    color: "#FFF7ED",
    fontSize: 22,
    fontWeight: "900",
  },
  ghostButton: {
    backgroundColor: "rgba(30, 41, 59, 0.9)",
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  ghostButtonText: {
    color: "#E2E8F0",
    fontSize: 14,
    fontWeight: "800",
  },
});
