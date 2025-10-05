import { ThemeProvider } from "./components/ui/theme-provider";
import '@xyflow/react/dist/style.css';
import Router from "./router";
import { AppProvider } from "./components/app-provider";

export default function App() {
  const hardcodedUser = { id: "1", name: "Alice" };

  
  return (
     <AppProvider initialUser={hardcodedUser}>
      <ThemeProvider>
        <Router />
      </ThemeProvider>
     </AppProvider>
  );
}

