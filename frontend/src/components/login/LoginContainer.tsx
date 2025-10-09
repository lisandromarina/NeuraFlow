import React from "react";
import { LoginComponent } from "./LoginComponent";
import { useAuth } from "@/context/AuthContext";
import { useApi } from "@/api/useApi";
import useFormState from "@/hooks/useFormState"; // import your TS hook

interface FormState {
  email: string;
  password: string;
}

export default function LoginContainer() {
  const { login } = useAuth();
  const { callApi } = useApi();

  // ✅ Use the hook instead of useState
  const { formData, handleChange, resetForm } = useFormState<FormState>({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // prevent page refresh
    console.log(formData);

    try {
      // Call your login API
      const response = await callApi("/auth/login", "POST", formData);

      // Assuming response contains token and user
      const { access_token } = response;

      // Save in context + localStorage
      login(access_token);

      // Optionally reset form
      resetForm();
    } catch (err) {
      console.error("Login failed:", err);
      alert("Invalid credentials");
    }
  };

  return (
    <LoginComponent handleSubmit={handleSubmit} handleChange={handleChange} />
  );
}
