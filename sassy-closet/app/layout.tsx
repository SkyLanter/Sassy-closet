import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Allura, Nunito } from "next/font/google";
import "./globals.css";

const nunito = Nunito({
  subsets: ["latin", "vietnamese"],
  variable: "--font-nunito",
});

const allura = Allura({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-allura",
});

export const metadata: Metadata = {
  title: "Sassy Closet",
  description:
    "Nhập ảnh, size, màu, link shop. App tự cấp mã Sassy Closet và caption Facebook để copy.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi" className={`${nunito.variable} ${allura.variable} h-full antialiased`}>
      <body className="sassy-shell min-h-full font-sans">{children}</body>
    </html>
  );
}
