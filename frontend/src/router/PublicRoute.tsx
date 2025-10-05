import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { AppContext } from "../components/app-provider"; // adjust path

const PublicRoute: React.FC = () => {
  const { user } = useContext(AppContext); // get user from context

  // If user exists, redirect to homepage
  if (user) {
    return <Navigate to="/workflow" replace />;
  }

  // Otherwise, render the public route
  return <Outlet />;
};

export default PublicRoute;
