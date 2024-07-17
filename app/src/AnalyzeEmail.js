import React, { useState, useRef } from "react";
import { Link } from "react-router-dom";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Analyze.css";

function AnalyzeEmailForm() {
  const [subject, setSubject] = useState("");
  const [sender, setSender] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const quillRef = useRef(null);

  // onchange function
  const onSubjectChange = (e) => setSubject(e.target.value);
  const onSenderChange = (e) => setSender(e.target.value);
  const onBodyChange = (value) => setBody(value);

  // Email body available toolbar options
  const toolbarOptions = [
    [{ size: ["small", false, "large", "huge"] }],
    ["bold", "italic", "underline"],
    [{ color: [] }],
    [{ align: [] }, { list: "ordered" }, { list: "bullet" }],
    ["link"],
    ["clean"],
  ];

  // Submit override
  const onSubmit = (e) => {
    e.preventDefault();

    const plaintextBody = quillRef.current.getEditor().getText();
    if (!body || plaintextBody === "\n") {
      setError("Body is required.");
      return;
    }
    setError("");

    const parser = new DOMParser();
    const doc = parser.parseFromString(body, "text/html");
    const htmlBody = doc.body.innerHTML;

    console.log({
      subject,
      sender,
      body: plaintextBody,
      html: htmlBody,
    });
  };

  return (
    <div className="analyze">
      <form autocomplete="off" onSubmit={onSubmit} className="text-size4">
        <nav>
          <Link to="/">
            <FontAwesomeIcon icon="fa-solid fa-xmark" />
          </Link>
        </nav>

        <h3>Enter Email Content</h3>
        <p>Analysis works best with all 3 fields provided.</p>

        <div class="field">
          <input
            type="text"
            name="subject"
            value={subject}
            onChange={onSubjectChange}
            placeholder="Subject"
          />
        </div>

        <div class="field">
          <input
            type="text"
            name="sender"
            value={sender}
            onChange={onSenderChange}
            placeholder="Sender <sender@email.com>"
          />
        </div>

        <div class="field">
          <label>
            Body: <i>(Required)</i>
          </label>
          <ReactQuill
            ref={quillRef}
            value={body}
            onChange={onBodyChange}
            theme="snow"
            modules={{
              toolbar: toolbarOptions,
            }}
          />
        </div>

        {error && <p className="text-secondary">{error}</p>}
        <button type="submit" class="text-size4">
          Analyze
        </button>
      </form>
    </div>
  );
}

export default AnalyzeEmailForm;
