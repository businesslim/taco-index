import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Influencer Indexes",
  description:
    "Track market sentiment from leading investors, executives, and economists worldwide. Scores are based on their public social media posts, reflecting how bullish or bearish the top financial voices are on crypto, stocks, gold, and macro trends.",
  openGraph: {
    title: "Influencer Indexes | TACO Index",
    description:
      "Track market sentiment from leading investors, executives, and economists worldwide. Scores are based on their public social media posts, reflecting how bullish or bearish the top financial voices are on crypto, stocks, gold, and macro trends.",
    url: "https://taco-index.com/influencers",
  },
  twitter: {
    card: "summary_large_image",
    title: "Influencer Indexes | TACO Index",
    description:
      "Track market sentiment from leading investors, executives, and economists worldwide. Scores are based on their public social media posts, reflecting how bullish or bearish the top financial voices are on crypto, stocks, gold, and macro trends.",
  },
};

export default function InfluencersLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
