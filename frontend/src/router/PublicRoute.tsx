import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext"; // adjust path

const PublicRoute: React.FC = () => {
  const { token, loading } = useAuth();

  // Show nothing or a loader while checking token
  if (loading) return null;

  // If user is logged in (token exists), redirect to protected page
  if (token) {
    return <Navigate to="/workflow" replace />;
  }

  // Otherwise, render the public route
  return <Outlet />;
};

export default PublicRoute;
