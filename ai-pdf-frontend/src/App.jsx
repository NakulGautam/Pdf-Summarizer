import { useState } from "react";
import axios from "axios";
import "./styles.css";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const uploadPDF = async () => {
    if (!file) {
      alert("Select a PDF first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      );

      setSummary(response.data.summary);
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>AI PDF Summarizer</h1>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={uploadPDF}>
        {loading ? "Processing..." : "Upload PDF"}
      </button>

      {summary && (
        <div className="summary">
          <h2>Summary</h2>
          <ul>
  {summary
    .split("\n")
    .filter((line) => line.trim())
    .map((line, index) => (
      <li key={index}>{line.replace("•", "").trim()}</li>
    ))}
</ul>
        </div>
      )}
    </div>
  );
}

export default App;