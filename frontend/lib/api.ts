const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface CurrentIndex {
  index_value: number;
  band_label: string;
  band_color: string;
  tweet_count: number;
  calculated_at: string | null;
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

export async function fetchIndexHistory(
  range: "7d" | "30d" | "all" = "7d"
): Promise<IndexHistoryPoint[]> {
  const res = await fetch(`${API_BASE}/api/index/history?range=${range}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Failed to fetch history");
  const data = await res.json();
  return data.data;
}
