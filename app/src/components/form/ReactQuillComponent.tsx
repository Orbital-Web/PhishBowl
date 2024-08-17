import dynamic from "next/dynamic";

import ReactQuill, { ReactQuillProps } from "react-quill";
import "react-quill/dist/quill.snow.css";

export type ReactQuillEditor = ReactQuill.UnprivilegedEditor;

const ReactQuillComponent = dynamic(
  async () => {
    const { default: RQ } = await import("react-quill");
    const Component = ({ ...props }: ReactQuillProps) => <RQ {...props} />;
    Component.displayName = "ReactQuillComponent";
    return Component;
  },
  {
    ssr: false,
    loading: () => <textarea></textarea>,
  }
);
export default ReactQuillComponent;
