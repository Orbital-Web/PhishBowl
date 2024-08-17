export interface EmailAnalysisRequest {
  sender: string | null;
  subject: string | null;
  body: string;
}
export type AnalysisLabel = "PHISHING" | "LEGITIMATE";
export interface AnalysisResult {
  label: AnalysisLabel;
  confidence: number;
}

export default async function AnalyzeEmail(
  email: EmailAnalysisRequest | File
): Promise<AnalysisResult> {
  let request;
  if (email instanceof File) {
    const data = new FormData();
    data.append("file", email);
    request = fetch("/api/analyze/image", { method: "POST", body: data });
  } else {
    request = fetch("/api/analyze/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(email),
    });
  }

  return request.then((response) => {
    if (!response.ok)
      throw new Error(
        `API request failed (${response.status})\n` +
          `URL: ${response.url}\n` +
          `Details: ${response.statusText}`
      );
    return response.json();
  });
}
