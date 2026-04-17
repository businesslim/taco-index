import { InfluencerIndexItem } from "@/lib/influencer-api";

const BAND_COLORS: Record<string, string> = {
  "Extreme Bullish": "#008000",
  "Bullish": "#22c55e",
  "Neutral": "#FFD700",
  "Bearish": "#FF8C00",
  "Extreme Bearish": "#FF4444",
};

export function InfluencerCard({ item }: { item: InfluencerIndexItem }) {
  const color = BAND_COLORS[item.band] ?? "#FFD700";
  return (
    <div
      className="bg-slate-800 rounded-lg p-3"
      style={{ borderLeft: `3px solid ${color}` }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm">
          {item.name[0]}
        </div>
        <div>
          <div className="text-slate-100 text-sm font-semibold">{item.name}</div>
          <div className="text-slate-500 text-xs">
            @{item.handle} · {item.domain}
          </div>
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-black" style={{ color }}>{item.score}</span>
        <span className="text-xs" style={{ color }}>{item.band.toUpperCase()}</span>
      </div>
      <div className="text-slate-600 text-xs mt-0.5">
        72h avg · {item.post_count_72h} post{item.post_count_72h !== 1 ? "s" : ""}
      </div>
      {item.latest_tweet && (
        <div className="mt-2 pt-2 border-t border-slate-700">
          <div className="text-slate-500 text-xs mb-1">Latest post</div>
          {item.latest_tweet_id ? (
            <a
              href={`https://x.com/${item.handle}/status/${item.latest_tweet_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 text-xs leading-relaxed line-clamp-2 hover:text-slate-200 transition-colors cursor-pointer"
            >
              {item.latest_tweet}
            </a>
          ) : (
            <div className="text-slate-400 text-xs leading-relaxed line-clamp-2">
              {item.latest_tweet}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
