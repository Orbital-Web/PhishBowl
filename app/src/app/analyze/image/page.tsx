"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

import styles from "../page.module.css";

export default function AnalyzeImagePage() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
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

    const data = new FormData();
    data.append("file", file as File);
    const response = await fetch("/api/analyze/image", {
      method: "POST",
      body: data,
    });
    if (response.status !== 200) {
      setError("Something went wrong. Please try again.");
      return;
    }
    const json = await response.json();
    router.push(`/analyze/result/?response=${JSON.stringify(json)}`);
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

        {error && <p className="text-secondary">{error}</p>}
        <button type="submit" className="text-size4">
          Analyze
        </button>
      </form>
    </div>
  );
}
