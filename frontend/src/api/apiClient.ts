import axios from "axios";
import type { AxiosInstance, AxiosResponse } from "axios";

const apiClient: AxiosInstance = axios.create({
  baseURL: "http://localhost:8000", // change this
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: interceptors
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    // Use set method to safely assign header
    config.headers = config.headers ?? {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});


apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    console.error("API error:", error);
    return Promise.reject(error);
  }
);

export default apiClient;
