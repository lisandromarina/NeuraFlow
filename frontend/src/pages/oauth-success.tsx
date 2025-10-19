"use client";

import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function OAuthSuccessPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const provider = params.get("provider");

    // If this is for authentication (has token)
    if (token) {
      login(token);
      navigate("/workflow");
      return;
    }

    // If this is for connecting services (has provider)
    if (provider) {
      // Send message to the opener window
      if (window.opener) {
        window.opener.postMessage(
          { success: true, provider, message: `${provider} connected!` },
          window.location.origin
        );
        window.close(); // close the popup
      }
    }
  }, []);

  return (
    <div className="w-full h-screen flex items-center justify-center bg-secondary">
      <div className="p-8 bg-card rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold mb-2">Authentication Successful!</h1>
        <p className="text-muted-foreground">Redirecting you to the application...</p>
      </div>
    </div>
  );
}
