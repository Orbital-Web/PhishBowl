export interface EmailUploadRequest {
  sender: string | null;
  subject: string | null;
  body: string;
  label: number;
}
export interface UploadResult {}

export default async function UploadEmail(
  email: EmailUploadRequest | File
): Promise<UploadResult> {
  let request;
  if (email instanceof File) {
    const data = new FormData();
    data.append("file", email);
    request = fetch("/api/phishbowl/add_image?label=1&anonymize=true", {
      method: "POST",
      body: data,
    });
  } else {
    request = fetch("/api/phishbowl/add_one?anonymize=true", {
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
