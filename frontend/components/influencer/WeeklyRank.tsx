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
        <div className="flex flex-col gap-1.5">
          {topBull.map((entry, i) => (
            <div key={entry.handle} className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="text-amber-400 text-xs w-3">{i + 1}</span>
                <span className="text-foreground text-xs">{entry.name}</span>
              </div>
              <span className="text-green-400 text-xs font-bold">{entry.avg_score} ▲</span>
            </div>
          ))}
          {topBull.length > 0 && topBear.length > 0 && (
            <div className="border-t border-border my-1" />
          )}
          {topBear.map((entry, i) => (
            <div key={entry.handle} className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground text-xs w-3">{i + 1}</span>
                <span className="text-foreground text-xs">{entry.name}</span>
              </div>
              <span className="text-red-400 text-xs font-bold">{entry.avg_score} ▼</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
