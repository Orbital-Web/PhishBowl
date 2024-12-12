import styles from "./ui.module.css";
import Link, { LinkProps } from "next/link";

export default function BackButton({ ...props }: LinkProps) {
  return (
    <Link {...props}>
      <h3 className={styles.backbutton}>&laquo; Back</h3>
    </Link>
  );
}
