import styles from "./form.module.css";

interface TextFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {}
export default function TextField({ ...props }: TextFieldProps) {
  return <input type="text" className={styles.textField} {...props}></input>;
}
