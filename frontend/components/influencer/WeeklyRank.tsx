import Image from "next/image";
import { WeeklyRankEntry } from "@/lib/influencer-api";
import { Card, CardContent } from "@/components/ui/card";

function getWeekRange(): string {
  const today = new Date();
  const day = today.getDay();
  const monday = new Date(today);
  monday.setDate(today.getDate() - (day === 0 ? 6 : day - 1));
  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  const fmt = (d: Date) =>
    d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  return `${fmt(monday)} – ${fmt(sunday)}`;
}

function Avatar({ entry }: { entry: WeeklyRankEntry }) {
  return (
    <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center text-xs overflow-hidden flex-shrink-0">
      {entry.profile_image_url ? (
        <Image
          src={entry.profile_image_url}
          alt={entry.name}
          width={24}
          height={24}
          className="w-full h-full object-cover"
          unoptimized
        />
      ) : (
        entry.name[0]
      )}
    </div>
  );
}

function RankList({
  entries,
  type,
}: {
  entries: WeeklyRankEntry[];
  type: "bull" | "bear";
}) {
  const isBull = type === "bull";
  return (
    <div>
      <p className={`text-xs font-semibold mb-2 ${isBull ? "text-green-400" : "text-red-400"}`}>
        {isBull ? "🐂 Most Bullish" : "🐻 Most Bearish"}
      </p>
      <div className="flex flex-col gap-1.5">
        {entries.map((entry, i) => (
          <div key={entry.handle} className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className={`text-xs w-3 ${isBull ? "text-amber-400" : "text-muted-foreground"}`}>
                {i + 1}
              </span>
              <Avatar entry={entry} />
              <span className="text-foreground text-xs">{entry.name}</span>
            </div>
            <span className={`text-xs font-bold ${isBull ? "text-green-400" : "text-red-400"}`}>
              {entry.avg_score} {isBull ? "▲" : "▼"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function WeeklyRank({
  topBull,
  topBear,
}: {
  topBull: WeeklyRankEntry[];
  topBear: WeeklyRankEntry[];
}) {
  return (
    <Card>
      <CardContent>
        <p className="text-muted-foreground text-xs font-bold tracking-widest uppercase mb-1">
          Weekly Rank
        </p>
        <p className="text-muted-foreground/60 text-xs mb-4">{getWeekRange()}</p>
        <div className="flex flex-col gap-4">
          {topBull.length > 0 && <RankList entries={topBull} type="bull" />}
          {topBull.length > 0 && topBear.length > 0 && (
            <div className="border-t border-border" />
          )}
          {topBear.length > 0 && <RankList entries={topBear} type="bear" />}
        </div>
      </CardContent>
    </Card>
  );
}
