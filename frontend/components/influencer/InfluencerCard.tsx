import Image from "next/image";
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
      className="bg-card rounded-lg p-3 ring-1 ring-foreground/10"
      style={{ borderLeft: `3px solid ${color}` }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm overflow-hidden flex-shrink-0">
          {item.profile_image_url ? (
            <Image
              src={item.profile_image_url}
              alt={item.name}
              width={32}
              height={32}
              className="w-full h-full object-cover"
              unoptimized
            />
          ) : (
            item.name[0]
          )}
        </div>
        <div>
          <div className="text-foreground text-sm font-semibold">{item.name}</div>
          <div className="text-muted-foreground text-xs">
            @{item.handle} · {item.domain}
          </div>
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-black" style={{ color }}>{item.score}</span>
        <span className="text-xs" style={{ color }}>{item.band.toUpperCase()}</span>
      </div>
      <div className="text-muted-foreground/60 text-xs mt-0.5">
        72h avg · {item.post_count_72h} post{item.post_count_72h !== 1 ? "s" : ""}
      </div>
      {item.latest_tweet && (
        <div className="mt-2 pt-2 border-t border-border">
          <div className="text-muted-foreground text-xs mb-1">Latest post</div>
          {item.latest_tweet_id ? (
            <a
              href={`https://x.com/${item.handle}/status/${item.latest_tweet_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground text-xs leading-relaxed line-clamp-2 hover:text-foreground transition-colors cursor-pointer"
            >
              {item.latest_tweet}
            </a>
          ) : (
            <div className="text-muted-foreground text-xs leading-relaxed line-clamp-2">
              {item.latest_tweet}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
