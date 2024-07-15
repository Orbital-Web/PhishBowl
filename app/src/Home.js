import React from "react";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Home.css";

function Home() {
  return (
    <div className="analyze">
      <div className="header">
        <h1>Analyze with PhishNet</h1>
        <p className="subtext">
          PhishNet may anonymize and add your email to the PhishBowl to prevent
          similar phishing scams in the future. You may disable this in your
          settings.
        </p>
      </div>

      <div className="options">
        <Link to="/image">
          <button>
            <h2>
              <FontAwesomeIcon icon="fa-image" />
            </h2>
            <p>Email Screenshot</p>
          </button>
        </Link>

        <Link to="/email">
          <button>
            <h2>
              <FontAwesomeIcon icon="fa-t" />
            </h2>
            <p>Email Text</p>
          </button>
        </Link>
      </div>
    </div>
  );
}

export default Home;
