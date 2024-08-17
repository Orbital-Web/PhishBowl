"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Delta } from "quill";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

import AnalyzeEmail from "@/lib/api/analyzeAPI";
import ReactQuillComponent, {
  ReactQuillEditor,
} from "@/components/form/ReactQuillComponent";
import { SubmitButton } from "@/components/form/FormElements";
import styles from "../page.module.css";

export default function AnalyzeEmailPage() {
  const [subject, setSubject] = useState("");
  const [sender, setSender] = useState("");
  const [htmlBody, setHtmlBody] = useState("");
  const [plaintextBody, setPlaintextBody] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // onchange functions
  const onSubjectChange = (e: React.FormEvent<HTMLInputElement>) =>
    setSubject(e.currentTarget.value);
  const onSenderChange = (e: React.FormEvent<HTMLInputElement>) =>
    setSender(e.currentTarget.value);
  const onBodyChange = (
    value: string,
    delta: Delta,
    source: string,
    editor: ReactQuillEditor
  ) => {
    setHtmlBody(value);
    setPlaintextBody(editor.getText());
  };

  // email body toolbar options
  const toolbarOptions = [
    [{ size: ["small", false, "large", "huge"] }],
    ["bold", "italic", "underline"],
    [{ color: [] }],
    [{ align: [] }, { list: "ordered" }, { list: "bullet" }],
    ["link"],
    ["clean"],
  ];

  // submit override
  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (plaintextBody === "\n") {
      setError("Body is required.");
      return;
    }

    const email = {
      sender,
      subject,
      body: plaintextBody,
    };
    setLoading(true);
    const result = await AnalyzeEmail(email)
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

        <h3>Enter Email Content</h3>
        <p>Analysis works best with all 3 fields provided.</p>

        <div className={styles.field}>
          <input
            type="text"
            name="subject"
            value={subject}
            onChange={onSubjectChange}
            placeholder="Subject"
            autoComplete="off"
          />
        </div>

        <div className={styles.field}>
          <input
            type="text"
            name="sender"
            value={sender}
            onChange={onSenderChange}
            placeholder="Sender <sender@email.com>"
            autoComplete="off"
          />
        </div>

        <div className={styles.field}>
          <label>
            Body: <i>(Required)</i>
          </label>
          <ReactQuillComponent
            value={htmlBody}
            onChange={onBodyChange}
            theme="snow"
            modules={{
              toolbar: toolbarOptions,
            }}
          />
        </div>

        {error && <p className="text-error">{error}</p>}
        <SubmitButton text="Analyze" loading={loading}></SubmitButton>
      </form>
    </div>
  );
}
