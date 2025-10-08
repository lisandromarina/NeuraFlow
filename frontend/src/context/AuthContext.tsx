import React, { createContext, useContext, useEffect, useState } from "react";
import { useApi } from "../api/useApi";

interface AuthContextType {
  token: string | null;
  email?: string;
  login: (token: string, email?: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | undefined>(undefined);
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
    if (email) {
      setEmail(email);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setEmail(undefined);
  };

  return (
    <AuthContext.Provider value={{ token, email, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};
