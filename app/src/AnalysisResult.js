// src/ResultsPage.js
import React, { useEffect, useState } from "react";
import { Form, useLocation, useNavigate } from "react-router-dom";
import Chart from "react-apexcharts";
import "./AnalysisResult.css";

function colerp(start, end, value) {
  const r = Math.round(start.r + (end.r - start.r) * value);
  const g = Math.round(start.g + (end.g - start.g) * value);
  const b = Math.round(start.b + (end.b - start.b) * value);

  return `rgb(${r}, ${g}, ${b})`;
}

function AnalysisGauge({ label, confidence }) {
  const phishcolor = { r: 255, g: 97, b: 136 };
  const legitcolor = { r: 120, g: 220, b: 232 };
  const valuecolor = "#ADA6A0";

  const fillcolor =
    label === "PHISHING"
      ? colerp({ r: 255, g: 216, b: 102 }, phishcolor, confidence)
      : colerp({ r: 255, g: 216, b: 102 }, legitcolor, confidence);
  const animTime = 1000 * Math.pow(confidence, 1 / 3);

  const options = {
    chart: {
      height: 100,
      type: "radialBar",
      fontFamily: "eurostile",
      animations: {
        enabled: true,
        speed: animTime,
      },
    },

    plotOptions: {
      radialBar: {
        startAngle: -145,
        endAngle: 145,
        hollow: {
          size: "40%",
        },
        track: {
          background: "#1E1F1C",
          dropShadow: {
            enabled: true,
            opacity: 0.15,
          },
        },
        dataLabels: {
          name: {
            offsetY: 120,
            fontSize: "1.5rem",
          },
          value: {
            offsetY: 76,
            formatter: function (val) {
              return Number.parseFloat(val).toFixed(2) + "%";
            },
            color: valuecolor,
            fontSize: "1rem",
          },
        },
      },
    },
    series: [confidence * 100],
    labels: [label],
    colors: [fillcolor],
  };

  return (
    <Chart
      options={options}
      series={options.series}
      type={options.chart.type}
    />
  );
}

function ResultsPage() {
  const location = useLocation();
  const state = location.state;
  const [progress, setProgress] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  // Call backend api for analysis
  useEffect(() => {
    const analyzeData = async () => {
      if (!state) return;

      setProgress("Analyzing email...");

      let response;
      if (state.type === "email") {
        const data = {
          sender: state.sender,
          subject: state.subject,
          body: state.body,
        };
        response = await fetch("/api/analyze/email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
      } else {
        const data = new FormData();
        data.append("file", state.file);
        response = await fetch("/api/analyze/image", {
          method: "POST",
          body: data,
        });
      }
      const result = await response.json();

      // FIXME: mock result
      // const result = {
      //   label: Math.random() >= 0.5 ? "PHISHING" : "LEGITIMATE",
      //   confidence: Math.random(),
      //   details: { ai: 0.73, similarity: 0.85, impersonation: 0.9, link: 0.8 },
      // };

      setResult(result);
    };

    analyzeData();
  }, [state]);

  // redirect navigation without state
  if (!state) {
    navigate("/");
    return;
  }

  return (
    <div className="results">
      {!result && <div className="progress">{progress}</div>}

      {result && (
        <div className="results-summary">
          <h2 className="subtext">Analysis Results</h2>
          <div className="result-gauge">
            <AnalysisGauge
              label={result.label}
              confidence={result.confidence}
            />
          </div>
        </div>
      )}
      {result && (
        <details className="result-details">
          <summary>Details</summary>
          <article>AAA</article>
        </details>
      )}
    </div>
  );
}

export default ResultsPage;
