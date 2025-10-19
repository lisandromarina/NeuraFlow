import React from "react";
import RegisterComponent from "./RegisterComponent";
import { useNavigate } from "react-router-dom";
import { useApi } from "@/api/useApi";
import useFormState from "@/hooks/useFormState";

interface FormState {
  email: string;
  password: string;
  confirmPassword: string;
}

export default function RegisterContainer() {
  const navigate = useNavigate();
  const { callApi } = useApi();

  // Use the hook for form state management
  const { formData, handleChange, resetForm } = useFormState<FormState>({
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // prevent page refresh

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      // Call your register API
      await callApi("/auth/register", "POST", {
        email: formData.email,
        password: formData.password,
      });

      // Reset form
      resetForm();

      // Show success message
      alert("Registration successful! Please login with your credentials.");

      // Redirect to login page
      navigate("/login");
    } catch (err) {
      console.error("Registration failed:", err);
      alert("Registration failed. Please try again.");
    }
  };

  return (
    <RegisterComponent handleSubmit={handleSubmit} handleChange={handleChange} />
  );
}

