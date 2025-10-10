import { ThemeProvider } from "./components/ui/theme-provider";
import '@xyflow/react/dist/style.css';
import Router from "./router";
import { AuthProvider } from "./context/AuthContext"; 
import { WorkflowProvider } from "./context/WorkflowContext";

export default function App() {
  return (
     <AuthProvider>
      <WorkflowProvider>
        <ThemeProvider>
          <Router />
        </ThemeProvider>
      </WorkflowProvider>
     </AuthProvider>
  );
}

