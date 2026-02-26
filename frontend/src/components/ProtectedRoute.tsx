import { Navigate } from "react-router-dom";

interface Props {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: Props) => {
  const token = localStorage.getItem("access_token");

  console.log("ProtectedRoute token:", token);

  if (!token) {
    console.log("No token → redirecting");
    return <Navigate to="/login" replace />;
  }

  console.log("Token exists → allow");
  return <>{children}</>;
};

export default ProtectedRoute;