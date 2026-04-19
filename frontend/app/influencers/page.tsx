"use client";

import { useEffect, useState } from "react";
import {
  fetchInfluencerSummary,
  fetchInfluencers,
  InfluencerSummary,
  InfluencerIndexItem,
} from "@/lib/influencer-api";
import { AssetExpertSentiment } from "@/components/influencer/AssetExpertSentiment";
import { BullBearRatio } from "@/components/influencer/BullBearRatio";
import { WeeklyRank } from "@/components/influencer/WeeklyRank";
import { InfluencerCard } from "@/components/influencer/InfluencerCard";
import { CategoryFilter } from "@/components/influencer/CategoryFilter";
import { SortControl, SortKey } from "@/components/influencer/SortControl";

export default function InfluencersPage() {
  const [summary, setSummary] = useState<InfluencerSummary | null>(null);
  const [influencers, setInfluencers] = useState<InfluencerIndexItem[]>([]);
  const [category, setCategory] = useState<string | null>(null);
  const [sort, setSort] = useState<SortKey>("score_desc");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchInfluencerSummary(), fetchInfluencers()]).then(
      ([s, inf]) => {
        setSummary(s);
        setInfluencers(inf);
        setLoading(false);
      }
    );
  }, []);

  const handleCategoryChange = async (cat: string | null) => {
    setCategory(cat);
    const filtered = await fetchInfluencers(cat ?? undefined);
    setInfluencers(filtered);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Hero */}
      <div className="flex flex-col gap-1.5">
        <h2 className="text-lg font-semibold text-foreground">What is Influencer Indexes?</h2>
        <p className="text-muted-foreground text-sm leading-relaxed">
          Track market sentiment from leading investors, executives, and economists worldwide. Scores are based on their public social media posts, reflecting how bullish or bearish the top financial voices are on crypto, stocks, gold, and macro trends.
        </p>
      </div>

      {/* Asset Expert Sentiment */}
      {summary && <AssetExpertSentiment indexes={summary.asset_indexes} />}

      {/* Bull-Bear + Weekly Rank */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BullBearRatio data={summary.bull_bear_ratio} />
          <WeeklyRank
            topBull={summary.weekly_top_bull}
            topBear={summary.weekly_top_bear}
          />
        </div>
      )}

      {/* Card grid */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <div>
            <h2 className="text-foreground font-bold">Influencer Indexes</h2>
            <p className="text-muted-foreground text-xs">
              Real-time market sentiment · {influencers.length} global experts
            </p>
          </div>
        </div>
        <div className="flex flex-col gap-2 mb-3">
          <CategoryFilter selected={category} onChange={handleCategoryChange} />
          <SortControl value={sort} onChange={setSort} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {[...influencers]
            .sort((a, b) => {
              if (sort === "score_desc") return b.score - a.score;
              if (sort === "score_asc")  return a.score - b.score;
              const ta = a.latest_tweet_id ?? "";
              const tb = b.latest_tweet_id ?? "";
              if (sort === "updated_desc") return tb.localeCompare(ta);
              return ta.localeCompare(tb);
            })
            .map((item) => (
              <InfluencerCard key={item.handle} item={item} />
            ))}
        </div>
      </div>
    </div>
  );
}
