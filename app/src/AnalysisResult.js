// src/ResultsPage.js
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function ResultsPage() {
  const location = useLocation();
  const state = location.state;
  const [progress, setProgress] = useState("");
  const [result, setResult] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const navigate = useNavigate();

  //
  useEffect(() => {
    const analyzeData = async () => {
      if (!state) return;

      setProgress("Analyzing email...");
      console.log("A");

      let response;
      if (state.type === "email") {
        response = await fetch("/api/analyze/email", {
          method: "POST",
          redirect: "follow",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sender: state.sender,
            subject: state.subject,
            body: state.body,
          }),
        });
      } else {
        response = await fetch("/api/analyze/image", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            file: state.file,
          }),
        });
      }

      const result = await response.json();
      setResult(result);

      setTimeout(() => setShowResult(true), 500); // Delay to trigger animation
    };

    analyzeData();
  }, [state]);

  // redirect navigation without state
  if (!state) {
    navigate("/");
    return;
  }

  return (
    <div className="results-container">
      {!result && <div className="progress">{progress}</div>}

      {showResult && result && (
        <div className="results-box">
          <h2>Analysis Results</h2>
          <p>Label: {result.label}</p>
          <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}

export default ResultsPage;
