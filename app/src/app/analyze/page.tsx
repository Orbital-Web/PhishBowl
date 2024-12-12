import { faImage, faT } from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import BackButton from "@/components/ui/BackButton";
import SquareButton from "@/components/ui/SquareButton";
import styles from "./page.module.css";

export default function AnalyzePage() {
  return (
    <div className={styles.home}>
      <BackButton href={getRoutes("home")} />
      <div className={styles.header}>
        <h1 className="text-primary">Analyze with PhishNet</h1>
        <p className="subtext">
          PhishNet will use an AI to compare your email to other submitted
          emails to determine whether it is a phish or benign.
        </p>
      </div>

      <div className={styles.options}>
        <SquareButton
          theme="tertiary"
          href={getRoutes("analyzeImage")}
          label="Analyze Screenshot"
          icon={faImage}
        />
        <SquareButton
          theme="tertiary"
          href={getRoutes("analyzeEmail")}
          label="Analyze Text"
          icon={faT}
        />
      </div>
    </div>
  );
}
