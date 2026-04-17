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

export default function InfluencersPage() {
  const [summary, setSummary] = useState<InfluencerSummary | null>(null);
  const [influencers, setInfluencers] = useState<InfluencerIndexItem[]>([]);
  const [category, setCategory] = useState<string | null>(null);
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
            <h2 className="text-slate-100 font-bold">Influencer Indexes</h2>
            <p className="text-slate-500 text-xs">
              Real-time market sentiment · {influencers.length} global experts
            </p>
          </div>
        </div>
        <CategoryFilter selected={category} onChange={handleCategoryChange} />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mt-3">
          {influencers.map((item) => (
            <InfluencerCard key={item.handle} item={item} />
          ))}
        </div>
      </div>
    </div>
  );
}
