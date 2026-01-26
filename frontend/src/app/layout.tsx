import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    template: "%s | Todo App",
    default: "Todo App - Task Management",
  },
  description: "Full-stack web todo application with authentication and persistent storage",
  keywords: ["todo", "task management", "productivity", "authentication"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
