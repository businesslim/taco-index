const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface CurrentIndex {
  index_value: number;
  band_label: string;
  band_color: string;
  tweet_count: number;
  calculated_at: string | null;
  last_post_at: string | null;
}

export interface TweetWithScore {
  tweet_id: string;
  source: string;
  content: string;
  posted_at: string;
  final_score: number;
  band_label: string;
  band_color: string;
  llm_reasoning: string;
  market_relevant: boolean;
}

export interface IndexHistoryPoint {
  index_value: number;
  band_label: string;
  calculated_at: string;
}

export async function fetchCurrentIndex(): Promise<CurrentIndex> {
  const res = await fetch(`${API_BASE}/api/index/current`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Failed to fetch index");
  return res.json();
}

export async function fetchRecentTweets(limit = 20): Promise<TweetWithScore[]> {
  const res = await fetch(`${API_BASE}/api/tweets/recent?limit=${limit}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Failed to fetch tweets");
  const data = await res.json();
  return data.data;
}

export interface MarketAsset {
  symbol: string;
  label: string;
  price: number;
  change_percent: number;
}

export interface MarketPrices {
  equities: MarketAsset[];
  commodities: MarketAsset[];
}

export async function fetchMarketPrices(): Promise<MarketPrices> {
  try {
    const res = await fetch(`${API_BASE}/api/market/prices`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return { equities: [], commodities: [] };
    return res.json();
  } catch {
    return { equities: [], commodities: [] };
  }
}

export async function fetchIndexHistory(
  range: "1d" | "7d" | "30d" | "all" = "7d"
): Promise<IndexHistoryPoint[]> {
  try {
    const res = await fetch(`${API_BASE}/api/index/history?range=${range}`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.data ?? [];
  } catch {
    return [];
  }
}

export interface AssetPoint {
  t: string;
  price: number;
}

export interface AssetHistory {
  btc: AssetPoint[];
  spx: AssetPoint[];
  gold: AssetPoint[];
}

export async function fetchAssetHistory(
  range: "1d" | "7d" | "30d" = "7d"
): Promise<AssetHistory> {
  try {
    const res = await fetch(`${API_BASE}/api/market/history?range=${range}`, {
      cache: "no-store",
    });
    if (!res.ok) return { btc: [], spx: [], gold: [] };
    return res.json();
  } catch {
    return { btc: [], spx: [], gold: [] };
  }
}
