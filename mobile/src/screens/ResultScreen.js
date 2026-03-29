import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";

import ActionCard from "../components/ActionCard";

const RISK_COLORS = {
  LOW: "#22C55E",
  MEDIUM: "#F59E0B",
  HIGH: "#EF4444",
  PENDING: "#38BDF8",
};

export default function ResultScreen({ navigation, route }) {
  const { result, inputText } = route.params;
  const accent = RISK_COLORS[result.risk] || "#F59E0B";
  const alcohol = result.parsed_data.alcohol;
  const needsMoreInfo = result.status === "needs_more_info";
  const guidance = result.guidance || {};

  return (
    <LinearGradient colors={["#07101D", "#0F172A", "#18263F"]} style={styles.bg}>
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.label}>{needsMoreInfo ? "More details needed" : "Final guidance"}</Text>
          <View style={[styles.banner, { borderColor: accent }]}> 
            <Text style={[styles.riskText, { color: accent }]}>{needsMoreInfo ? "ADD A LITTLE MORE" : `${result.risk} RISK`}</Text>
            <Text style={styles.summary}>{result.summary}</Text>
          </View>

          <View style={styles.messagePanel}>
            <Text style={styles.messageTitle}>{needsMoreInfo ? "What is missing" : "Assistant message"}</Text>
            <Text style={styles.messageBody}>{result.assistant_message}</Text>
          </View>

          <View style={styles.panel}>
            <Text style={styles.panelTitle}>What was entered</Text>
            <Text style={styles.body}>{inputText}</Text>
          </View>

          {needsMoreInfo ? (
            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Please go back and add</Text>
              {result.follow_up_questions.map((question) => (
                <ActionCard key={question} title="Add this on the home screen" body={question} accent={accent} />
              ))}
            </View>
          ) : (
            <>
              {guidance.what_is_happening ? (
                <View style={styles.panel}>
                  <Text style={styles.panelTitle}>What is happening</Text>
                  <Text style={styles.body}>{guidance.what_is_happening}</Text>
                </View>
              ) : null}

              <Section title="Do now" items={guidance.do_now} accent={accent} />
              <Section title="Eat next" items={guidance.eat_next} accent={accent} />
              <Section title="Drink now" items={guidance.drink_now} accent={accent} />
              <Section title="Avoid" items={guidance.avoid} accent={accent} />
              <Section title="Check again" items={guidance.check_again} accent={accent} />
              <Section title="Get help now if" items={guidance.when_to_get_help} accent={accent} />

              <View style={styles.panel}>
                <Text style={styles.panelTitle}>Why this result</Text>
                {result.reasons.map((reason) => (
                  <ActionCard key={reason} title="Reason" body={reason} accent={accent} />
                ))}
              </View>

              {result.knowledge?.length ? (
                <View style={styles.panel}>
                  <Text style={styles.panelTitle}>Why the app says this</Text>
                  {result.knowledge.map((item) => (
                    <Text key={item} style={styles.knowledgeText}>{item}</Text>
                  ))}
                </View>
              ) : null}

              {result.daily_memory?.entries_today ? (
                <View style={styles.panel}>
                  <Text style={styles.panelTitle}>Today so far</Text>
                  <Text style={styles.body}>{result.daily_memory.summary}</Text>
                </View>
              ) : null}

              {alcohol?.explanation ? (
                <View style={styles.panel}>
                  <Text style={styles.panelTitle}>Alcohol size guide</Text>
                  <Text style={styles.body}>
                    {alcohol.explanation} Detected amount: {alcohol.alcohol_units} units.
                  </Text>
                </View>
              ) : null}
            </>
          )}

          <Text style={styles.disclaimer}>Guidance only. Seek urgent care if symptoms are severe or readings are dangerous.</Text>

          <Pressable onPress={() => navigation.navigate("Home")} style={styles.primaryButton}>
            <Text style={styles.primaryLabel}>{needsMoreInfo ? "Back to questions" : "Back home"}</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

function Section({ title, items, accent }) {
  if (!items?.length) return null;
  return (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{title}</Text>
      {items.map((item) => (
        <ActionCard key={`${title}-${item}`} title={title} body={item} accent={accent} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1 },
  safe: { flex: 1 },
  content: {
    padding: 20,
    paddingBottom: 32,
  },
  label: {
    color: "#F59E0B",
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 1.2,
    marginBottom: 12,
    textTransform: "uppercase",
  },
  banner: {
    backgroundColor: "rgba(15, 23, 42, 0.9)",
    borderRadius: 24,
    borderWidth: 2,
    padding: 20,
  },
  riskText: {
    fontSize: 30,
    fontWeight: "900",
    marginBottom: 10,
  },
  summary: {
    color: "#E2E8F0",
    fontSize: 18,
    lineHeight: 26,
  },
  messagePanel: {
    backgroundColor: "rgba(249, 115, 22, 0.14)",
    borderRadius: 24,
    marginTop: 18,
    padding: 18,
  },
  messageTitle: {
    color: "#FDBA74",
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 10,
  },
  messageBody: {
    color: "#FFF7ED",
    fontSize: 18,
    lineHeight: 26,
  },
  panel: {
    backgroundColor: "rgba(15, 23, 42, 0.72)",
    borderRadius: 24,
    marginTop: 18,
    padding: 18,
  },
  panelTitle: {
    color: "#F8FAFC",
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 12,
  },
  body: {
    color: "#CBD5E1",
    fontSize: 17,
    lineHeight: 24,
  },
  knowledgeText: {
    color: "#D6E3F3",
    fontSize: 16,
    lineHeight: 23,
    marginBottom: 10,
  },
  disclaimer: {
    color: "#FCA5A5",
    fontSize: 14,
    lineHeight: 20,
    marginTop: 18,
  },
  primaryButton: {
    alignItems: "center",
    backgroundColor: "#F97316",
    borderRadius: 16,
    marginTop: 18,
    paddingVertical: 16,
  },
  primaryLabel: {
    color: "#FFF7ED",
    fontSize: 18,
    fontWeight: "800",
  },
});
