import axios from "axios";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";
// const API_URL =
//   process.env.EXPO_PUBLIC_API_URL ||
//   "https://pulseai-api.onrender.com";

// Keep Render awake by pinging every 10 minutes
setInterval(() => {
  axios.get(`${API_URL}/health`).catch(() => {});
}, 10 * 60 * 1000);


export async function analyzeText(text) {
  const response = await axios.post(`${API_URL}/analyze`, { text }, { timeout: 30000 });
  return response.data;
}

export async function fetchHistory() {
  const response = await axios.get(`${API_URL}/history`);
  return response.data;
}
