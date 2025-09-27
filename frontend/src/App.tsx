import Layout from "./components/layout";
import { ThemeProvider } from "./components/ui/theme-provider";
import '@xyflow/react/dist/style.css';

export default function App() {
  return (
    <ThemeProvider >
      <Layout />
    </ThemeProvider>
  );
}

