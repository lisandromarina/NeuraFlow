import React, { createContext, useContext, useEffect, useState } from "react";
import { useApi } from "../api/useApi";

interface AuthContextType {
  token: string | null;
  email?: string;
  userId?: number;
  login: (token: string, email?: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper function to decode JWT token
const decodeToken = (token: string) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Error decoding token:", error);
    return null;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | undefined>(undefined);
  const [userId, setUserId] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  const { callApi } = useApi();

  useEffect(() => {
    const storedToken = localStorage.getItem("token");

    if (storedToken) {
      const validateToken = async () => {
        try {
          const response = await callApi("/auth/validate-token", "GET", undefined, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          });

          if (response.valid) {
            setToken(storedToken);
            setEmail(response.email);
            // Decode token to get user_id
            const decoded = decodeToken(storedToken);
            if (decoded && decoded.user_id) {
              setUserId(decoded.user_id);
            }
          } else {
            logout();
          }
        } catch (err) {
          console.warn("Token invalid or expired:", err);
          logout();
        } finally {
          setLoading(false);
        }
      };
      validateToken();
    } else {
      setLoading(false);
    }
  }, []);

  const login = (newToken: string, email?: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    
    // Decode token to extract user_id and email
    const decoded = decodeToken(newToken);
    if (decoded) {
      if (decoded.user_id) {
        setUserId(decoded.user_id);
      }
      if (decoded.sub && !email) {
        setEmail(decoded.sub); // 'sub' typically contains the email
      }
    }
    
    if (email) {
      setEmail(email);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setEmail(undefined);
    setUserId(undefined);
  };

  return (
    <AuthContext.Provider value={{ token, email, userId, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};
