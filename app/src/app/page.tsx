import Link from "next/link";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faImage, faT } from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <div className={styles.home}>
      <div className={styles.header}>
        <h1 className="text-primary">Analyze with PhishNet</h1>
        <p className="subtext">
          PhishNet may anonymize and add your email to the PhishBowl to prevent
          similar phishing scams in the future. You may disable this in your
          settings.
        </p>
      </div>

      <div className={styles.options}>
        <Link href={getRoutes("imageAnalysis")}>
          <button>
            <h2>
              <FontAwesomeIcon icon={faImage} />
            </h2>
            <p>Analyze Screenshot</p>
          </button>
        </Link>

        <Link href={getRoutes("emailAnalysis")}>
          <button>
            <h2>
              <FontAwesomeIcon icon={faT} />
            </h2>
            <p>Analyze Text</p>
          </button>
        </Link>
      </div>
    </div>
  );
}
