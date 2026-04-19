const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface InfluencerIndexItem {
  handle: string;
  name: string;
  category: string;
  domain: string;
  score: number;
  band: string;
  calculated_at: string | null;
  latest_tweet: string | null;
  latest_tweet_id: string | null;
  latest_tweet_posted_at: string | null;
  post_count_72h: number;
  profile_image_url: string | null;
}

export interface AssetExpertIndex {
  asset: string;
  score: number;
  band: string;
  bull_count: number;
  bear_count: number;
  neutral_count: number;
  total_count: number;
  calculated_at: string | null;
}

export interface BullBearRatio {
  bull_count: number;
  bear_count: number;
  neutral_count: number;
  total_count: number;
}

export interface WeeklyRankEntry {
  handle: string;
  name: string;
  avg_score: number;
  rank_bull: number | null;
  rank_bear: number | null;
  profile_image_url: string | null;
}

export interface InfluencerSummary {
  asset_indexes: AssetExpertIndex[];
  bull_bear_ratio: BullBearRatio;
  weekly_top_bull: WeeklyRankEntry[];
  weekly_top_bear: WeeklyRankEntry[];
}

export async function fetchInfluencerSummary(): Promise<InfluencerSummary> {
  try {
    const res = await fetch(`${API_BASE}/api/influencer/summary`, {
      next: { revalidate: 1800 },
    });
    if (!res.ok) return { asset_indexes: [], bull_bear_ratio: { bull_count: 0, bear_count: 0, neutral_count: 0, total_count: 0 }, weekly_top_bull: [], weekly_top_bear: [] };
    return res.json();
  } catch {
    return { asset_indexes: [], bull_bear_ratio: { bull_count: 0, bear_count: 0, neutral_count: 0, total_count: 0 }, weekly_top_bull: [], weekly_top_bear: [] };
  }
}

export async function fetchInfluencers(category?: string): Promise<InfluencerIndexItem[]> {
  try {
    const url = category
      ? `${API_BASE}/api/influencer?category=${encodeURIComponent(category)}`
      : `${API_BASE}/api/influencer`;
    const res = await fetch(url, { next: { revalidate: 1800 } });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}
