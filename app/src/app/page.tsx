import {
  faCloudArrowUp,
  faMagnifyingGlass,
} from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import SquareButton from "@/components/ui/SquareButton";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <div className={styles.home}>
      <div className={styles.header}>
        <h1 className="text-neutral">PhishNet</h1>
        <p className="subtext">
          Analyze an email for phishing scams using PhishNet, or upload an email
          containing a known scam to the PhishBowl to improve the analysis.
        </p>
      </div>

      <div className={styles.options}>
        <SquareButton
          theme="primary"
          href={getRoutes("analyze")}
          label="Analyze Email"
          icon={faMagnifyingGlass}
        />
        <SquareButton
          theme="secondary"
          href={getRoutes("upload")}
          label="Upload to PhishBowl"
          icon={faCloudArrowUp}
        />
      </div>
    </div>
  );
}
