import { Pressable, StyleSheet, Text, View } from "react-native";

export default function MicButton({ isListening, onPress, transcript }) {
  return (
    <Pressable onPress={onPress} style={[styles.button, isListening ? styles.buttonActive : null]}>
      <View style={styles.iconWrap}>
        <Text style={styles.icon}>{isListening ? "REC" : "MIC"}</Text>
      </View>
      <Text style={styles.label}>{isListening ? "Listening now" : "Tap to speak"}</Text>
      <Text style={styles.helper}>
        {transcript ? transcript : "Say: rice and sweets, BP 150/95, sugar 180, 2 glasses water, feeling normal"}
      </Text>
      <Text style={styles.cta}>{isListening ? "Tap again to stop" : "Voice note for faster logging"}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: "rgba(248, 250, 252, 0.08)",
    borderColor: "rgba(255,255,255,0.14)",
    borderRadius: 28,
    borderWidth: 1,
    minHeight: 184,
    padding: 22,
  },
  buttonActive: {
    backgroundColor: "rgba(220, 38, 38, 0.22)",
    borderColor: "rgba(252, 165, 165, 0.42)",
  },
  iconWrap: {
    alignItems: "center",
    alignSelf: "flex-start",
    backgroundColor: "rgba(249, 115, 22, 0.18)",
    borderRadius: 16,
    justifyContent: "center",
    marginBottom: 16,
    minHeight: 52,
    minWidth: 72,
    paddingHorizontal: 14,
  },
  icon: {
    color: "#FFF7ED",
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: 1,
  },
  label: {
    color: "#F8FAFC",
    fontSize: 28,
    fontWeight: "900",
    marginBottom: 10,
  },
  helper: {
    color: "#E2E8F0",
    fontSize: 15,
    lineHeight: 23,
  },
  cta: {
    color: "#FDBA74",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 14,
  },
});
