import React from "react";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Analyze.css";

function AnalyzeImageForm() {
  return (
    <div className="analyze">
      <form className="text-size4">
        <nav>
          <Link to="/">
            <FontAwesomeIcon icon="fa-solid fa-xmark" />
          </Link>
        </nav>

        <h3>Upload Email Screenshot</h3>
        <input type="file" />

        <button type="submit" class="text-size4">
          Analyze
        </button>
      </form>
    </div>
  );
}

export default AnalyzeImageForm;
