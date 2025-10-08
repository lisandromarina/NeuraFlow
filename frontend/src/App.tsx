import { ThemeProvider } from "./components/ui/theme-provider";
import '@xyflow/react/dist/style.css';
import Router from "./router";
import { AuthProvider } from "./context/AuthContext"; 

export default function App() {
  return (
     <AuthProvider>
      <ThemeProvider>
        <Router />
      </ThemeProvider>
     </AuthProvider>
  );
}

