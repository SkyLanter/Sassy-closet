import type { Viewport } from "next";
import { Be_Vietnam_Pro, Cormorant_Garamond } from "next/font/google";
import { rootSeo } from "@/lib/seo";
import "./globals.css";

const sans = Be_Vietnam_Pro({
  variable: "--font-be-vietnam",
  subsets: ["latin", "latin-ext", "vietnamese"],
  weight: ["300", "400", "500", "600"],
  display: "swap",
});

const display = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin", "latin-ext", "vietnamese"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const viewport: Viewport = {
  viewportFit: "cover",
  themeColor: "#111111",
  colorScheme: "light",
};

export async function generateMetadata() {
  return rootSeo();
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${sans.variable} ${display.variable} h-full min-h-dvh antialiased`}
    >
      <body className="flex min-h-full min-h-dvh flex-col bg-paper font-sans text-ink">
        {children}
      </body>
    </html>
  );
}