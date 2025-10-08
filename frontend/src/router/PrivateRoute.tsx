import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext"; // adjust path

const PrivateRoute: React.FC = () => {
  const { token, loading } = useAuth();

  // While checking token, render nothing or a loader
  if (loading) return null;

  // If not logged in, redirect to login page
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // If logged in, render the protected route
  return <Outlet />;
};

export default PrivateRoute;
