import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { AppContext } from "../components/app-provider"; // make sure path is correct

const PrivateRoute: React.FC = () => {
  const { user } = useContext(AppContext); // get user from context

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default PrivateRoute;
