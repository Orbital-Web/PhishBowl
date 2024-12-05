import type { Metadata } from "next";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { config } from "@fortawesome/fontawesome-svg-core";
config.autoAddCss = false;
import "./globals.css";

import UNUFooter from "@/components/ui/UNUFooter";

export const metadata: Metadata = {
  title: "PhishNet",
  description: "Analyze with PhishNet",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
        <UNUFooter />
      </body>
    </html>
  );
}
