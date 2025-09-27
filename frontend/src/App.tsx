import Layout from "./components/layout";
import { ThemeProvider } from "./components/ui/theme-provider";

export default function App() {
  return (
    <ThemeProvider >
      <Layout />
    </ThemeProvider>
  );
}

