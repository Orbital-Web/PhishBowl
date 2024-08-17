"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

import AnalyzeEmail from "@/lib/api/analyzeAPI";
import { SubmitButton } from "@/components/form/FormElements";
import styles from "../page.module.css";

export default function AnalyzeImagePage() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onFileChange = (e: React.FormEvent<HTMLInputElement>) => {
    if (e.currentTarget.files) {
      const selectedFile = e.currentTarget.files![0];
      const validTypes = ["image/png", "image/jpeg", "image/tiff"];
      const isValid = validTypes.includes(selectedFile.type);
      if (isValid) {
        setFile(selectedFile);
        setError("");
      } else {
        setFile(null);
        setError("Invalid file type. Please upload a supported image type.");
      }
    }
  };

  // submit override
  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (file === null) {
      setError("Please upload an image.");
      return;
    }

    setLoading(true);
    const result = await AnalyzeEmail(file)
      .finally(() => setLoading(false))
      .catch((error) => {
        setError("Something went wrong. Please try again.");
        throw error;
      });
    router.push(`/analyze/result/?response=${JSON.stringify(result)}`);
  };

  return (
    <div className={styles.analyze}>
      <form onSubmit={onSubmit} className="text-size4">
        <nav>
          <Link href="/">
            <FontAwesomeIcon icon={faXmark} />
          </Link>
        </nav>

        <h3>Upload Email Screenshot</h3>

        <input
          type="file"
          accept="image/jpeg,image/png,image/tiff"
          onChange={onFileChange}
          required
        />

        {error && <p className="text-error">{error}</p>}
        <SubmitButton text="Analyze" loading={loading}></SubmitButton>
      </form>
    </div>
  );
}
