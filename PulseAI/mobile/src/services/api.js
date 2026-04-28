import axios from "axios";

// const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";
const API_URL = process.env.EXPO_PUBLIC_API_KEY || "https://pulseai-api.onrender.com";


export async function analyzeText(text) {
  const response = await axios.post(`${API_URL}/analyze`, { text });
  return response.data;
}

export async function fetchHistory() {
  const response = await axios.get(`${API_URL}/history`);
  return response.data;
}
