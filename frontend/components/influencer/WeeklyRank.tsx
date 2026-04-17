import { WeeklyRankEntry } from "@/lib/influencer-api";

export function WeeklyRank({
  topBull,
  topBear,
}: {
  topBull: WeeklyRankEntry[];
  topBear: WeeklyRankEntry[];
}) {
  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-3">
        Weekly Rank
      </p>
      <div className="flex flex-col gap-1.5">
        {topBull.map((entry, i) => (
          <div key={entry.handle} className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-amber-400 text-xs w-3">{i + 1}</span>
              <span className="text-slate-200 text-xs">{entry.name}</span>
            </div>
            <span className="text-green-400 text-xs font-bold">{entry.avg_score} ▲</span>
          </div>
        ))}
        {topBull.length > 0 && topBear.length > 0 && (
          <div className="border-t border-slate-700 my-1" />
        )}
        {topBear.map((entry, i) => (
          <div key={entry.handle} className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-slate-500 text-xs w-3">{i + 1}</span>
              <span className="text-slate-200 text-xs">{entry.name}</span>
            </div>
            <span className="text-red-400 text-xs font-bold">{entry.avg_score} ▼</span>
          </div>
        ))}
      </div>
    </div>
  );
}
