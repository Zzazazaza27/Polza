import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Polza Companies — Каталог компаний",
  description: "Каталог компаний из внутренней базы Polza Agency с поиском и фильтрацией",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
