import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

const apiClient: AxiosInstance = axios.create({
  baseURL: "https://your-api-base-url.com", // change this
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: interceptors
apiClient.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
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
