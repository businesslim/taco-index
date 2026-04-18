import { BullBearRatio as BullBearRatioType } from "@/lib/influencer-api";
import { Card, CardContent } from "@/components/ui/card";

const SIZE = 160;
const STROKE = 18;
const R = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * R;
const GAP = 2;

function arcStyle(pct: number, offset: number) {
  const filled = Math.max(0, (pct / 100) * CIRCUMFERENCE - GAP);
  return {
    strokeDasharray: `${filled} ${CIRCUMFERENCE - filled}`,
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

  const segments = [
    { color: "#22c55e", label: "Bullish", count: bull_count, pct: bullPct },
    { color: "#FFD700", label: "Neutral", count: neutral_count, pct: neutralPct },
    { color: "#FF4444", label: "Bearish", count: bear_count, pct: bearPct },
  ];

  return (
    <Card>
      <CardContent>
        <p className="text-muted-foreground text-xs font-bold tracking-widest uppercase mb-4">
          Bull / Bear Ratio
        </p>

        <div className="flex justify-center mb-4">
          <div className="relative" style={{ width: SIZE, height: SIZE }}>
            <svg width={SIZE} height={SIZE} style={{ transform: "rotate(-90deg)" }}>
              <circle
                cx={SIZE / 2} cy={SIZE / 2} r={R}
                fill="none" stroke="currentColor" strokeWidth={STROKE}
                className="text-muted/50"
              />
              <circle cx={SIZE / 2} cy={SIZE / 2} r={R} fill="none" stroke="#22c55e" strokeWidth={STROKE} strokeLinecap="butt" style={arcStyle(bullPct, 0)} />
              <circle cx={SIZE / 2} cy={SIZE / 2} r={R} fill="none" stroke="#FFD700" strokeWidth={STROKE} strokeLinecap="butt" style={arcStyle(neutralPct, bullPct)} />
              <circle cx={SIZE / 2} cy={SIZE / 2} r={R} fill="none" stroke="#FF4444" strokeWidth={STROKE} strokeLinecap="butt" style={arcStyle(bearPct, bullPct + neutralPct)} />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-black leading-none" style={{ color: dominant.color }}>
                {Math.round(dominant.pct)}%
              </span>
              <span className="text-muted-foreground text-xs mt-1">{dominant.label}</span>
              <span className="text-muted-foreground/60 text-xs">{total_count} experts</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 divide-x divide-border border border-border rounded-lg overflow-hidden">
          {segments.map(({ color, label, count, pct }) => (
            <div key={label} className="flex flex-col items-center py-2.5 px-1">
              <span className="text-xl font-black leading-none" style={{ color }}>{count}</span>
              <span className="text-xs font-semibold mt-0.5" style={{ color }}>{Math.round(pct)}%</span>
              <span className="text-muted-foreground text-xs mt-0.5">{label}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
