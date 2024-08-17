"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";

import { ApexOptions } from "apexcharts";

import { AnalysisLabel, AnalysisResult } from "@/lib/api/analyzeAPI";
import styles from "./page.module.css";

const ChartComponent = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

interface Color {
  r: number;
  g: number;
  b: number;
}
function colerp(start: Color, end: Color, value: number) {
  const r = Math.round(start.r + (end.r - start.r) * value);
  const g = Math.round(start.g + (end.g - start.g) * value);
  const b = Math.round(start.b + (end.b - start.b) * value);

  return `rgb(${r}, ${g}, ${b})`;
}

function AnalysisGauge({
  label,
  confidence,
}: {
  label: AnalysisLabel;
  confidence: number;
}) {
  const phishcolor = { r: 255, g: 97, b: 136 };
  const legitcolor = { r: 120, g: 220, b: 232 };
  const valuecolor = "#ADA6A0";

  const fillcolor =
    label === "PHISHING"
      ? colerp({ r: 255, g: 216, b: 102 }, phishcolor, confidence)
      : colerp({ r: 255, g: 216, b: 102 }, legitcolor, confidence);
  const animTime = 1000 * Math.pow(confidence, 1 / 3);

  const options: ApexOptions = {
    chart: {
      type: "radialBar",
      fontFamily: "eurostile",
      animations: {
        enabled: true,
        speed: animTime,
      },
      sparkline: {
        enabled: true,
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
            formatter: function (val: number) {
              return val.toFixed(2) + "%";
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
    <ChartComponent
      options={options}
      series={options.series}
      type={options.chart!.type}
    />
  );
}

function AnalysisResults() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const response = searchParams.get("response");
  if (response === null || response === "{}") {
    router.push("/");
    return;
  }
  const result: AnalysisResult = JSON.parse(response);

  return (
    <div className={styles.results}>
      <div className={styles.summary}>
        <h2 className="subtext">Analysis Results</h2>
        <div className={styles.gauge}>
          <AnalysisGauge label={result.label} confidence={result.confidence} />
        </div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <AnalysisResults />
    </Suspense>
  );
}
