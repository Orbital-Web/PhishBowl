import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Analyze.css";

function AnalyzeImageForm() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const onFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = ["image/png", "image/jpeg", "image/tiff"];
      const isValid = validTypes.includes(selectedFile.type);
      if (isValid) {
        setFile(selectedFile);
        setError("");
      } else {
        setFile(null);
        setError("Invalid file type. Please select a supported image type.");
      }
    }
  };

  // submit override
  const onSubmit = (e) => {
    e.preventDefault();

    const state = {
      type: "image",
      file,
    };
    navigate("/result", { state });
  };

  return (
    <div className="analyze">
      <form onSubmit={onSubmit} className="text-size4">
        <nav>
          <Link to="/">
            <FontAwesomeIcon icon="fa-solid fa-xmark" />
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
        <button type="submit" class="text-size4">
          Analyze
        </button>
      </form>
    </div>
  );
}

export default AnalyzeImageForm;
