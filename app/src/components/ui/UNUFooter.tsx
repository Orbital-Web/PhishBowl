import styles from "./ui.module.css";

export default function UNUFooter({ ...props }) {
  return (
    <div className={styles.unufooter}>
      <img src="/images/logo.png"></img>
      <h3 className="text">
        This is an initiative lead by the United Nations University
      </h3>
    </div>
  );
}
