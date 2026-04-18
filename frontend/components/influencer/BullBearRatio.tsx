import { BullBearRatio as BullBearRatioType } from "@/lib/influencer-api";

const SIZE = 120;
const STROKE = 14;
const R = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * R;

function arc(pct: number, offset: number) {
  return {
    strokeDasharray: `${(pct / 100) * CIRCUMFERENCE} ${CIRCUMFERENCE}`,
    strokeDashoffset: -((offset / 100) * CIRCUMFERENCE),
  };
}

export function BullBearRatio({ data }: { data: BullBearRatioType }) {
  const { bull_count, bear_count, neutral_count, total_count } = data;
  const bullPct = total_count > 0 ? (bull_count / total_count) * 100 : 0;
  const bearPct = total_count > 0 ? (bear_count / total_count) * 100 : 0;
  const neutralPct = 100 - bullPct - bearPct;

  const dominant =
    bullPct >= bearPct && bullPct >= neutralPct
      ? { label: "Bullish", pct: bullPct, color: "#22c55e" }
      : bearPct >= neutralPct
      ? { label: "Bearish", pct: bearPct, color: "#FF4444" }
      : { label: "Neutral", pct: neutralPct, color: "#FFD700" };

  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-3">
        Bull / Bear Ratio
      </p>
      <div className="flex items-center gap-5">
        {/* Donut */}
        <div className="relative flex-shrink-0" style={{ width: SIZE, height: SIZE }}>
          <svg width={SIZE} height={SIZE} style={{ transform: "rotate(-90deg)" }}>
            {/* Track */}
            <circle
              cx={SIZE / 2} cy={SIZE / 2} r={R}
              fill="none" stroke="#1e293b" strokeWidth={STROKE}
            />
            {/* Bull */}
            <circle
              cx={SIZE / 2} cy={SIZE / 2} r={R}
              fill="none" stroke="#22c55e" strokeWidth={STROKE}
              strokeLinecap="butt"
              style={arc(bullPct, 0)}
            />
            {/* Neutral */}
            <circle
              cx={SIZE / 2} cy={SIZE / 2} r={R}
              fill="none" stroke="#FFD700" strokeWidth={STROKE}
              strokeLinecap="butt"
              style={arc(neutralPct, bullPct)}
            />
            {/* Bear */}
            <circle
              cx={SIZE / 2} cy={SIZE / 2} r={R}
              fill="none" stroke="#FF4444" strokeWidth={STROKE}
              strokeLinecap="butt"
              style={arc(bearPct, bullPct + neutralPct)}
            />
          </svg>
          {/* Center label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-lg font-black leading-none" style={{ color: dominant.color }}>
              {Math.round(dominant.pct)}%
            </span>
            <span className="text-slate-500 text-xs mt-0.5">{dominant.label}</span>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-col gap-2.5 flex-1">
          {[
            { color: "#22c55e", label: "Bullish", count: bull_count, pct: bullPct },
            { color: "#FFD700", label: "Neutral", count: neutral_count, pct: neutralPct },
            { color: "#FF4444", label: "Bearish", count: bear_count, pct: bearPct },
          ].map(({ color, label, count, pct }) => (
            <div key={label} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
              <span className="text-slate-400 text-xs flex-1">{label}</span>
              <span className="text-xs font-bold" style={{ color }}>{count}</span>
              <span className="text-slate-600 text-xs w-9 text-right">{Math.round(pct)}%</span>
            </div>
          ))}
          <div className="border-t border-slate-700 pt-1.5 mt-0.5">
            <span className="text-slate-600 text-xs">{total_count} experts total</span>
          </div>
        </div>
      </div>
    </div>
  );
}
