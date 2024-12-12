import { faImage, faT } from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import SquareButton from "@/components/ui/SquareButton";
import styles from "./page.module.css";
import BackButton from "@/components/ui/BackButton";

export default function UploadPage() {
  return (
    <div className={styles.home}>
      <BackButton href={getRoutes("home")} />
      <div className={styles.header}>
        <h1 className="text-secondary">Upload to PhishBowl</h1>
        <p className="subtext">
          Your email will be anonymized when adding them to the PhishBowl.
          Uploading an email will help PhishBowl detect similar emails in the
          future.
        </p>
      </div>

      <div className={styles.options}>
        <SquareButton
          theme="tertiary"
          href={getRoutes("uploadImage")}
          label="Upload Screenshot"
          icon={faImage}
        />
        <SquareButton
          theme="tertiary"
          href={getRoutes("uploadEmail")}
          label="Upload Text"
          icon={faT}
        />
      </div>
    </div>
  );
}
