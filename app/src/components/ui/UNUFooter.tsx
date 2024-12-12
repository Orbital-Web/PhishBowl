import styles from "./ui.module.css";
import Link from "next/link";
import getRoutes from "@/lib/routes/routes";

export default function UNUFooter() {
  return (
    <Link href={getRoutes("credits")}>
      <div className={styles.unufooter}>
        <img src="/images/logo.png"></img>
        <h3 className="text">AI-powered Phish Bowl Developed by UNU</h3>
      </div>
    </Link>
  );
}
