import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button"

function App() {
  const [data, setData] = useState("");
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    console.log(`${apiUrl}/`)
    fetch(`${apiUrl}/`)
      .then((response) => response.json())
      .then((data) => setData(data.message))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="flex min-h-svh flex-col items-center justify-center">
      <Button>Click me</Button>
    </div>
  );
}

export default App;
