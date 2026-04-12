import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TACO Index — Trump Asset Crypto Oracle",
  description:
    "Real-time crypto sentiment index based on Trump's social media posts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-gray-950 text-white min-h-screen`}
      >
        <header className="border-b border-gray-800 px-6 py-4">
          <div className="max-w-5xl mx-auto flex items-center gap-2">
            <span className="text-2xl">🌮</span>
            <h1 className="text-xl font-bold">TACO Index</h1>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
