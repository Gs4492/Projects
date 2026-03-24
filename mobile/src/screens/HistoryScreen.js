import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useFocusEffect } from "@react-navigation/native";

import { fetchHistory } from "../services/api";

export default function HistoryScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchHistory();
      setItems(data);
    } catch (error) {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [loadHistory])
  );

  return (
    <LinearGradient colors={["#07101D", "#0F172A", "#18263F"]} style={styles.bg}>
      <SafeAreaView style={styles.safe}>
        <ScrollView
          contentContainerStyle={styles.content}
          refreshControl={<RefreshControl refreshing={loading} onRefresh={loadHistory} tintColor="#F97316" />}
        >
          <Text style={styles.title}>Recent entries</Text>
          <Text style={styles.subtitle}>This helps you review patterns and test the MVP quickly.</Text>

          {loading ? (
            <ActivityIndicator color="#F97316" size="large" style={styles.loader} />
          ) : items.length === 0 ? (
            <View style={styles.empty}>
              <Text style={styles.emptyText}>No logs yet. Analyze one entry first.</Text>
            </View>
          ) : (
            items.map((item) => (
              <View key={item.id} style={styles.card}>
                <Text style={styles.risk}>{item.risk}</Text>
                <Text style={styles.input}>{item.input_text}</Text>
                <Text style={styles.meta}>{String(item.created_at)}</Text>
              </View>
            ))
          )}

          <Pressable onPress={() => navigation.navigate("Home")} style={styles.button}>
            <Text style={styles.buttonLabel}>Back to home</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1 },
  safe: { flex: 1 },
  content: {
    padding: 20,
    paddingBottom: 32,
  },
  title: {
    color: "#F8FAFC",
    fontSize: 32,
    fontWeight: "800",
    marginBottom: 8,
  },
  subtitle: {
    color: "#CBD5E1",
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 18,
  },
  loader: {
    marginTop: 30,
  },
  empty: {
    backgroundColor: "#172033",
    borderRadius: 20,
    padding: 18,
  },
  emptyText: {
    color: "#CBD5E1",
    fontSize: 16,
  },
  card: {
    backgroundColor: "#172033",
    borderRadius: 20,
    marginBottom: 12,
    padding: 16,
  },
  risk: {
    color: "#F97316",
    fontSize: 14,
    fontWeight: "800",
    marginBottom: 8,
  },
  input: {
    color: "#F8FAFC",
    fontSize: 16,
    lineHeight: 23,
    marginBottom: 8,
  },
  meta: {
    color: "#94A3B8",
    fontSize: 13,
  },
  button: {
    alignItems: "center",
    backgroundColor: "#F97316",
    borderRadius: 16,
    marginTop: 18,
    paddingVertical: 16,
  },
  buttonLabel: {
    color: "#FFF7ED",
    fontSize: 17,
    fontWeight: "800",
  },
});
