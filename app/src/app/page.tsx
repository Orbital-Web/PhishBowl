import { faImage, faT } from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import SquareButton from "@/components/ui/SquareButton";
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
        <SquareButton
          theme="tertiary"
          href={getRoutes("imageAnalysis")}
          label="Analyze Screenshot"
          icon={faImage}
        />
        <SquareButton
          theme="tertiary"
          href={getRoutes("emailAnalysis")}
          label="Analyze Text"
          icon={faT}
        />
      </div>
    </div>
  );
}
