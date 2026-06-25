import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const hostsApi = {
  list: () => client.get("/api/hosts").then((res) => res.data),
  create: (payload) => client.post("/api/hosts", payload).then((res) => res.data),
  remove: (hostId) => client.delete(`/api/hosts/${hostId}`),
  ping: (hostId) => client.post(`/api/hosts/${hostId}/ping`).then((res) => res.data),
  metrics: (hostId) => client.get(`/api/hosts/${hostId}/metrics`).then((res) => res.data),
};

export const settingsApi = {
  get: () => client.get("/api/settings").then((res) => res.data),
  update: (payload) => client.put("/api/settings", payload).then((res) => res.data),
};

/** Extracts a display-safe string message from an Axios error, regardless of whether
 * the API returned `detail` as a string (HTTPException) or a list (Pydantic 422). */
export function getErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const msg = detail[0]?.msg;
    if (typeof msg === "string" && msg.trim()) {
      return msg.replace(/^Value error, /, "");
    }
  }
  return fallback;
}

export default client;
