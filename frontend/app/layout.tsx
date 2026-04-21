import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { DM_Mono } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { GoogleAnalytics } from "@next/third-parties/google";
import { Navbar } from "@/components/Navbar";
import { AuthProvider } from "@/components/AuthProvider";

const dmMono = DM_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: {
    default: "TACO Index — Real-Time Market Sentiment from Trump's Truth Social",
    template: "%s | TACO Index",
  },
  description:
    "Track how Donald Trump's Truth Social posts move financial markets. TACO Index scores each post for market relevance, giving real-time sentiment signals for crypto, equities, and commodities.",
  metadataBase: new URL("https://taco-index.com"),
  openGraph: {
    type: "website",
    siteName: "TACO Index",
    title: "TACO Index — Real-Time Market Sentiment from Trump's Truth Social",
    description:
      "Track how Donald Trump's Truth Social posts move financial markets. TACO Index scores each post for market relevance, giving real-time sentiment signals for crypto, equities, and commodities.",
    url: "https://taco-index.com",
  },
  twitter: {
    card: "summary_large_image",
    title: "TACO Index — Real-Time Market Sentiment from Trump's Truth Social",
    description:
      "Track how Donald Trump's Truth Social posts move financial markets. TACO Index scores each post for market relevance, giving real-time sentiment signals for crypto, equities, and commodities.",
  },
  verification: {
    google: "jr-iw4l_W94Aw1FZeWUB3-ZcsvESrlXBB3-6YhfE_-E",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn("dark font-sans", GeistSans.variable, dmMono.variable)}>
      <body className="bg-background text-foreground min-h-screen">
        <AuthProvider>
          <Navbar />
          <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
        </AuthProvider>
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
