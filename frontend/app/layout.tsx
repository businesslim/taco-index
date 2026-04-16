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
  title: "TACO Index — Real-Time Market Sentiment from Trump's Truth Social",
  description:
    "Track how Donald Trump's Truth Social posts move financial markets. TACO Index scores each post for market relevance, giving real-time sentiment signals for crypto, equities, and commodities.",
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
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🌮</span>
              <h1 className="text-xl font-bold">TACO Index</h1>
            </div>
            <a
              href="https://t.me/TACOIndexBot"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors"
              style={{
                backgroundColor: "#F59E0B22",
                color: "#F59E0B",
                border: "1px solid #F59E0B44",
              }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              Telegram Bot
            </a>
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
