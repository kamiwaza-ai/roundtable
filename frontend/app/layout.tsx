import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "RoundTable",
  description: "AI-powered group discussions and decision making",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <nav className="border-b p-4">
          <div className="max-w-4xl mx-auto flex gap-6">
            <Link href="/" className="font-bold">
              RoundTable
            </Link>
            <Link href="/agents" className="hover:text-primary">
              Agents
            </Link>
            <Link href="/round-tables" className="hover:text-primary">
              Round Tables
            </Link>
          </div>
        </nav>
        <div className="max-w-4xl mx-auto">
          {children}
        </div>
      </body>
    </html>
  );
}
