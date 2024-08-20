import dynamic from "next/dynamic";

import { ApexOptions } from "apexcharts";

import { AnalysisLabel } from "@/lib/api/analyzeAPI";
import { colerp } from "@/lib/color/color";

const ChartComponent = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

export function AnalysisGauge({
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
