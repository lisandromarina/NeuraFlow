import { ThemeProvider } from "./components/ui/theme-provider";
import '@xyflow/react/dist/style.css';
import Router from "./router";

export default function App() {
  return (
    <ThemeProvider>
      <Router />
    </ThemeProvider>
  );
}

