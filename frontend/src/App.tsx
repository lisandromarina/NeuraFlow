import { useEffect, useState } from "react";

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
    <div className="App">
      <h1>Frontend + Backend Test</h1>
      <p>Backend says: {data}</p>
    </div>
  );
}

export default App;
