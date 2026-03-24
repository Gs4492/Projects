import { StyleSheet, Text, View } from "react-native";

export default function ActionCard({ title, body, accent = "#F59E0B" }) {
  return (
    <View style={[styles.card, { borderColor: accent }]}> 
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#172033",
    borderRadius: 18,
    borderWidth: 1,
    marginBottom: 12,
    padding: 16,
  },
  title: {
    color: "#F8FAFC",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 6,
  },
  body: {
    color: "#C7D2FE",
    fontSize: 15,
    lineHeight: 22,
  },
});
