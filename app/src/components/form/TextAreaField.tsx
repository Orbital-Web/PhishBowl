import dynamic from "next/dynamic";

import ReactQuill, { ReactQuillProps } from "react-quill";
import "react-quill/dist/quill.snow.css";

import styles from "./form.module.css";
import { ReactElement } from "react";

export type TextAreaEditor = ReactQuill.UnprivilegedEditor;
const ReactQuillComponent = dynamic(
  async () => {
    const { default: RQ } = await import("react-quill");
    const Component = ({ ...props }: ReactQuillProps) => <RQ {...props} />;
    Component.displayName = "ReactQuillComponent";
    return Component;
  },
  {
    ssr: false,
    loading: () => <textarea className={styles.textAreaPlaceholder}></textarea>,
  }
);

interface TextAreaFieldProps extends ReactQuillProps {
  label: ReactElement | string;
}
export default function TextAreaField({ label, ...props }: TextAreaFieldProps) {
  const toolbarOptions = [
    [{ size: ["small", false, "large", "huge"] }],
    ["bold", "italic", "underline"],
    [{ color: [] }],
    [{ align: [] }, { list: "ordered" }, { list: "bullet" }],
    ["link"],
    ["clean"],
  ];

  return (
    <div className={styles.textAreaField}>
      <label className="text-size4">{label}</label>
      <ReactQuillComponent
        theme="snow"
        modules={{
          toolbar: toolbarOptions,
        }}
        {...props}
      />
    </div>
  );
}
