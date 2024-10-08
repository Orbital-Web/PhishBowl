import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

import styles from "./form.module.css";

interface SubmitButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  text: string;
  loading: boolean;
  theme: "primary" | "secondary";
}
export default function SubmitButton({
  text,
  loading,
  theme,
  ...props
}: SubmitButtonProps) {
  return (
    <button
      type="submit"
      className={
        `text-size4 ${styles.submitButton} ` +
        `${styles[loading ? `${theme}-load` : `${theme}`]}`
      }
      {...props}
      disabled={loading}
    >
      {loading ? (
        <FontAwesomeIcon icon={faSpinner} className="fa-spin"></FontAwesomeIcon>
      ) : (
        text
      )}
    </button>
  );
}
