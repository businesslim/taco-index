import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { DM_Mono } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { GoogleAnalytics } from "@next/third-parties/google";

const dmMono = DM_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-mono",
});


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
    <html lang="en" className={cn("dark font-sans", GeistSans.variable, dmMono.variable)}>
      <body className="bg-background text-foreground min-h-screen">
        <header className="border-b border-border px-6 py-4">
          <div className="max-w-5xl mx-auto flex items-center gap-2">
            <span className="text-2xl">🌮</span>
            <h1 className="text-xl font-bold">TACO Index</h1>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
      </body>
      <GoogleAnalytics gaId="G-F5LSGKHT55" />
      <script
        async
        src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5422727782996636"
        crossOrigin="anonymous"
      />
    </html>
  );
}
