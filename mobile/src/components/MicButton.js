import { Pressable, StyleSheet, Text, View } from "react-native";

export default function MicButton({ isListening, onPress, transcript }) {
  return (
    <Pressable onPress={onPress} style={[styles.button, isListening ? styles.buttonActive : null]}>
      <Text style={styles.icon}>{isListening ? "REC" : "MIC"}</Text>
      <Text style={styles.label}>{isListening ? "Listening... tap to stop" : "Tap to Speak"}</Text>
      <Text style={styles.helper}>
        {transcript ? transcript : "Say things like: rice and sweets, BP 150/95, sugar 180, 2 glasses water, feeling normal"}
      </Text>
      {isListening ? <View style={styles.pulse} /> : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: "center",
    backgroundColor: "#EA580C",
    borderRadius: 28,
    elevation: 2,
    justifyContent: "center",
    minHeight: 180,
    padding: 24,
    shadowColor: "#000",
    shadowOpacity: 0.18,
    shadowRadius: 16,
  },
  buttonActive: {
    backgroundColor: "#DC2626",
  },
  icon: {
    color: "#FFF7ED",
    fontSize: 28,
    fontWeight: "900",
    marginBottom: 10,
  },
  label: {
    color: "#FFF7ED",
    fontSize: 24,
    fontWeight: "800",
    marginBottom: 8,
    textAlign: "center",
  },
  helper: {
    color: "#FFF7ED",
    fontSize: 15,
    lineHeight: 22,
    opacity: 0.95,
    textAlign: "center",
  },
  pulse: {
    backgroundColor: "rgba(255,255,255,0.28)",
    borderRadius: 999,
    height: 18,
    marginTop: 14,
    width: 18,
  },
});
