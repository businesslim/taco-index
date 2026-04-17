import { AssetExpertIndex } from "@/lib/influencer-api";

const BAND_COLORS: Record<string, string> = {
  "Extreme Bullish": "#008000",
  "Bullish": "#22c55e",
  "Neutral": "#FFD700",
  "Bearish": "#FF8C00",
  "Extreme Bearish": "#FF4444",
};

const ASSET_LABELS: Record<string, string> = {
  crypto: "Crypto",
  stock: "Stock",
  gold: "Gold",
  macro: "Macro",
};

export function AssetExpertSentiment({ indexes }: { indexes: AssetExpertIndex[] }) {
  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-3">
        Asset Expert Sentiment · {indexes[0]?.total_count ?? 0}명 기준
      </p>
      <div className="flex flex-col gap-3">
        {indexes.map((idx) => {
          const color = BAND_COLORS[idx.band] ?? "#FFD700";
          return (
            <div key={idx.asset} className="flex items-center gap-3">
              <span className="text-slate-400 text-xs w-12">{ASSET_LABELS[idx.asset] ?? idx.asset}</span>
              <div className="flex-1 bg-slate-900 rounded h-2 overflow-hidden">
                <div
                  className="h-full rounded"
                  style={{ width: `${idx.score}%`, backgroundColor: color }}
                />
              </div>
              <span className="text-sm font-bold w-8" style={{ color }}>{idx.score}</span>
              <span className="text-xs w-24" style={{ color }}>{idx.band}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
