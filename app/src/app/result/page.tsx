"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { AnalysisResult } from "@/lib/api/analyzeAPI";
import { AnalysisGauge } from "@/components/results/Gauge";
import styles from "./page.module.css";

function AnalysisResults() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const response = searchParams.get("response");
  if (response === null) {
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
