"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

import { Delta } from "quill";

import UploadEmail from "@/lib/api/uploadAPI";
import getRoutes from "@/lib/routes/routes";
import FormCloseButton from "@/components/form/FormCloseButton";
import SubmitButton from "@/components/form/SubmitButton";
import TextAreaField, { TextAreaEditor } from "@/components/form/TextAreaField";
import TextField from "@/components/form/TextField";
import styles from "../shared.module.css";

export default function AnalyzeEmailPage() {
  const [subject, setSubject] = useState("");
  const [sender, setSender] = useState("");
  const [body, setBody] = useState("");
  const [htmlBody, setHtmlBody] = useState("");
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
    editor: TextAreaEditor
  ) => {
    setHtmlBody(value);
    setBody(editor.getText());
  };

  // submit override
  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (body === "" || body === "\n") {
      setError("Body is required.");
      return;
    }

    setLoading(true);
    const result = await UploadEmail({ sender, subject, body, label: 1.0 })
      .finally(() => setLoading(false))
      .catch((error) => {
        setError("Something went wrong. Please try again.");
        console.log(error);
      });
    if (result !== undefined) router.push(getRoutes("home"));
    // TODO: redirect to success page with stats & alerts
  };

  return (
    <div className={styles.analyze}>
      <form onSubmit={onSubmit}>
        <FormCloseButton href={getRoutes("upload")} />

        <h3>Upload Email</h3>
        <p>Please try to enter all 3 fields.</p>

        <TextField
          value={subject}
          onChange={onSubjectChange}
          placeholder="Subject"
          autoComplete="off"
        />

        <TextField
          value={sender}
          onChange={onSenderChange}
          placeholder="Sender <sender@email.com>"
          autoComplete="off"
        />

        <TextAreaField
          label={
            <>
              Body:<i className="text-error">*</i>
            </>
          }
          value={htmlBody}
          onChange={onBodyChange}
        />

        {error && <p className="text-error">{error}</p>}
        <SubmitButton
          theme="secondary"
          text="Upload"
          loading={loading}
        ></SubmitButton>
      </form>
    </div>
  );
}
