import React, { useState } from "react";
import { LoginComponent } from "./LoginComponent";
import { useAuth } from "@/context/AuthContext";
import { useApi } from "@/api/useApi";

interface FormState {
  email: string;
  password: string;
}

export default function LoginContainer() {
  const { login } = useAuth();
  const { callApi } = useApi();
  const [form, setForm] = useState<FormState>({ email: "", password: "" });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // ✅ prevent page refresh
    console.log(form);
    try {
      // Call your login API
      const response = await callApi("/auth/login", "POST", form);

      // Assuming response contains token and user
      const { access_token } = response;

      // Save in context + localStorage
      login(access_token);
    } catch (err) {
      console.error("Login failed:", err);
      alert("Invalid credentials");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <LoginComponent handleSubmit={handleSubmit} handleChange={handleChange} />
  );
}
