import { BullBearRatio as BullBearRatioType } from "@/lib/influencer-api";

export function BullBearRatio({ data }: { data: BullBearRatioType }) {
  const { bull_count, bear_count, neutral_count, total_count } = data;
  const bullPct = total_count > 0 ? (bull_count / total_count) * 100 : 0;
  const bearPct = total_count > 0 ? (bear_count / total_count) * 100 : 0;
  const neutralPct = 100 - bullPct - bearPct;

  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-3">
        Bull / Bear Ratio
      </p>
      <div className="flex gap-1 mb-3 h-2.5 rounded overflow-hidden">
        <div style={{ flex: bullPct, backgroundColor: "#22c55e" }} />
        <div style={{ flex: neutralPct, backgroundColor: "#FFD700" }} />
        <div style={{ flex: bearPct, backgroundColor: "#FF4444" }} />
      </div>
      <div className="flex justify-between">
        <div>
          <div className="text-green-400 text-xl font-black">{bull_count}</div>
          <div className="text-slate-500 text-xs">Bullish</div>
        </div>
        <div className="text-center">
          <div className="text-yellow-400 text-xl font-black">{neutral_count}</div>
          <div className="text-slate-500 text-xs">Neutral</div>
        </div>
        <div className="text-right">
          <div className="text-red-400 text-xl font-black">{bear_count}</div>
          <div className="text-slate-500 text-xs">Bearish</div>
        </div>
      </div>
    </div>
  );
}
