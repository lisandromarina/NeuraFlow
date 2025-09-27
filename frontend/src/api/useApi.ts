import { useState } from "react";
import apiClient from "./apiClient";
import type { AxiosRequestConfig } from "axios";

interface UseApiReturn<T> {
  callApi: (endpoint: string, method?: "GET" | "POST" | "PUT" | "DELETE", data?: any, config?: AxiosRequestConfig) => Promise<T>;
  loading: boolean;
  error: Error | null;
}

export const useApi = <T = any>(): UseApiReturn<T> => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const callApi = async (
    endpoint: string,
    method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
    data: any = null,
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    setLoading(true);
    setError(null);
    try {
      console.log(data)
      const response = await apiClient({
        url: endpoint,
        method,
        data,
        ...config,
      });
      return response.data;
    } catch (err: any) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { callApi, loading, error };
};
