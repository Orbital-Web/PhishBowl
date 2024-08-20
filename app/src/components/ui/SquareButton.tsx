import Link, { LinkProps } from "next/link";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { IconDefinition } from "@fortawesome/free-solid-svg-icons";

import styles from "./ui.module.css";

interface SquareButtonProps extends LinkProps {
  label: string;
  icon: IconDefinition;
  theme: "primary" | "secondary" | "tertiary";
}
export default function SquareButton({
  label,
  icon,
  theme,
  ...props
}: SquareButtonProps) {
  return (
    <Link className={styles.squareButton} {...props}>
      <button className={styles[theme]}>
        <h2>
          <FontAwesomeIcon icon={icon} />
        </h2>
        <p>{label}</p>
      </button>
    </Link>
  );
}
