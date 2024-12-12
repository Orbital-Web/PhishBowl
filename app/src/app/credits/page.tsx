import { faImage, faT } from "@fortawesome/free-solid-svg-icons";

import getRoutes from "@/lib/routes/routes";
import SquareButton from "@/components/ui/SquareButton";
import styles from "./page.module.css";
import BackButton from "@/components/ui/BackButton";

export default function CreditsPage() {
  return (
    <div className={styles.credits}>
      <BackButton href={getRoutes("home")} />
      <div className={styles.header}>
        <h1 className="text-primary">Credits</h1>
        <p className="subtext">
          This platform was developed by Rei Meguro under the support and
          supervision of Ng S. T. Chong as part of an initiative by the UNU to
          allow organizations to easily share phishing information with each
          other and detect new scams without compromising sensitive information.
        </p>
        <p className="subtext">
          The architecture of the platform along with the detection mechanism is
          published in the paper:{" "}
          <b>
            AdaPhish: AI-Powered Adaptive Defense and Education Resource Against
            Deceptive Emails
          </b>
        </p>
      </div>
    </div>
  );
}
