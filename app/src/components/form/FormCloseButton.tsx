import Link from "next/link";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

import styles from "./form.module.css";

interface FormCloseButtonProps {
  href: string;
}
export default function FormCloseButton({ href }: FormCloseButtonProps) {
  return (
    <nav className={`text-size4 ${styles.formCloseButton}`}>
      <Link href={href}>
        <FontAwesomeIcon icon={faXmark} />
      </Link>
    </nav>
  );
}
