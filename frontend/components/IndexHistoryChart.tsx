"use client";

import { useState, useEffect } from "react";
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import {
  IndexHistoryPoint,
  AssetPoint,
  fetchIndexHistory,
  fetchAssetHistory,
} from "@/lib/api";
import { Button } from "@/components/ui/button";

type Range = "1d" | "7d" | "30d";
type Granularity = "hour" | "day";

interface ChartPoint {
  key: string;
  label: string;
  tacoIndex: number;
  btcPct?: number;
  spxPct?: number;
  goldPct?: number;
}

function aggregateTaco(
  data: IndexHistoryPoint[],
  by: Granularity
): { key: string; value: number }[] {
  const buckets = new Map<string, number[]>();
  for (const d of data) {
    const dt = new Date(d.calculated_at);
    const key =
      by === "hour"
        ? dt.toISOString().slice(0, 13)
        : dt.toISOString().slice(0, 10);
    buckets.set(key, [...(buckets.get(key) ?? []), d.index_value]);
  }
  return Array.from(buckets.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, vals]) => ({
      key,
      value: Math.round(vals.reduce((a, b) => a + b, 0) / vals.length),
    }));
}

function buildPriceMap(data: AssetPoint[], by: Granularity): Map<string, number> {
  const map = new Map<string, number>();
  for (const d of data) {
    const dt = new Date(d.t);
    const key =
      by === "hour"
        ? dt.toISOString().slice(0, 13)
        : dt.toISOString().slice(0, 10);
    map.set(key, d.price);
  }
  return map;
}

function normalizeToPercent(
  priceMap: Map<string, number>,
  keys: string[]
): Map<string, number> {
  let base: number | null = null;
  const result = new Map<string, number>();
  for (const key of keys) {
    const price = priceMap.get(key);
    if (price === undefined) continue;
    if (base === null) base = price;
    result.set(key, parseFloat(((price - base) / base * 100).toFixed(2)));
  }
  return result;
}

function formatLabel(key: string, by: Granularity): string {
  if (by === "hour") {
    const dt = new Date(key + ":30:00Z");
    return dt.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  }
  const dt = new Date(key + "T12:00:00Z");
  return dt.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const RANGE_OPTIONS: { label: string; value: Range }[] = [
  { label: "1D", value: "1d" },
  { label: "7D", value: "7d" },
  { label: "30D", value: "30d" },
];

const ASSET_CONFIG = [
  { key: "btc" as const, label: "BTC", color: "#F7931A" },
  { key: "spx" as const, label: "S&P 500", color: "#818CF8" },
  { key: "gold" as const, label: "Gold", color: "#EAB308" },
];

type AssetKey = "btc" | "spx" | "gold";

export default function IndexHistoryChart() {
  const [range, setRange] = useState<Range>("7d");
  const [assets, setAssets] = useState<Record<AssetKey, boolean>>({
    btc: true,
    spx: true,
    gold: true,
  });
  const [indexData, setIndexData] = useState<IndexHistoryPoint[]>([]);
  const [assetData, setAssetData] = useState<{
    btc: AssetPoint[];
    spx: AssetPoint[];
    gold: AssetPoint[];
  }>({ btc: [], spx: [], gold: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchIndexHistory(range), fetchAssetHistory(range)]).then(
      ([idx, asset]) => {
        setIndexData(idx);
        setAssetData(asset);
        setLoading(false);
      }
    );
  }, [range]);

  const by: Granularity = range === "1d" ? "hour" : "day";
  const tacoAgg = aggregateTaco(indexData, by);
  const keys = tacoAgg.map((d) => d.key);

  const btcPct = normalizeToPercent(buildPriceMap(assetData.btc, by), keys);
  const spxPct = normalizeToPercent(buildPriceMap(assetData.spx, by), keys);
  const goldPct = normalizeToPercent(buildPriceMap(assetData.gold, by), keys);

  const chartData: ChartPoint[] = tacoAgg.map((d) => ({
    key: d.key,
    label: formatLabel(d.key, by),
    tacoIndex: d.value,
    btcPct: btcPct.get(d.key),
    spxPct: spxPct.get(d.key),
    goldPct: goldPct.get(d.key),
  }));

  const toggleAsset = (key: AssetKey) =>
    setAssets((prev) => ({ ...prev, [key]: !prev[key] }));

  const showRightAxis = ASSET_CONFIG.some((a) => assets[a.key]);

  const allPcts = chartData.flatMap((d) =>
    ASSET_CONFIG.filter((a) => assets[a.key])
      .map((a) => d[`${a.key}Pct` as keyof ChartPoint] as number | undefined)
      .filter((v): v is number => v !== undefined)
  );
  const pctPad = 3;
  const pctMin =
    allPcts.length > 0 ? Math.floor(Math.min(...allPcts) - pctPad) : -10;
  const pctMax =
    allPcts.length > 0 ? Math.ceil(Math.max(...allPcts) + pctPad) : 10;

  if (!loading && indexData.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">
        No history data yet. Check back after the first few pipeline runs.
      </p>
    );
  }

  return (
    <div>
      {/* Controls */}
      <div className="flex items-center justify-between mb-5 gap-3 flex-wrap">
        {/* Period tabs */}
        <div className="flex gap-1 bg-muted rounded-lg p-1">
          {RANGE_OPTIONS.map((opt) => (
            <Button
              key={opt.value}
              size="sm"
              variant={range === opt.value ? "secondary" : "ghost"}
              onClick={() => setRange(opt.value)}
              className="rounded-md"
            >
              {opt.label}
            </Button>
          ))}
        </div>

        {/* Asset toggles */}
        <div className="flex gap-2 flex-wrap">
          {ASSET_CONFIG.map(({ key, label, color }) => (
            <button
              key={key}
              onClick={() => toggleAsset(key)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                assets[key] ? "" : "text-muted-foreground border-border bg-transparent"
              }`}
              style={
                assets[key]
                  ? { backgroundColor: color + "22", color, borderColor: color + "66" }
                  : undefined
              }
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      {loading ? (
        <div className="h-72 flex items-center justify-center text-muted-foreground text-sm">
          Loading...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={288}>
          <ComposedChart
            data={chartData}
            margin={{ top: 5, right: showRightAxis ? 55 : 10, left: -20, bottom: 5 }}
          >
            <defs>
              {/*
                gradientUnits="userSpaceOnUse" + y1=5, y2=283:
                chart height=288, top/bottom margin=5 → drawing area y: 5~283
                value=100→y=5, 80→y=61, 60→y=116, 40→y=172, 20→y=227, 0→y=283
                → offset 20%=value80, 40%=value60, 60%=value40, 80%=value20
              */}
              <linearGradient id="tacoStrokeGradient" gradientUnits="userSpaceOnUse" x1="0" y1="5" x2="0" y2="283">
                <stop offset="0%"   stopColor="#008000" />
                <stop offset="20%"  stopColor="#008000" />
                <stop offset="20%"  stopColor="#32CD32" />
                <stop offset="40%"  stopColor="#32CD32" />
                <stop offset="40%"  stopColor="#FFD700" />
                <stop offset="60%"  stopColor="#FFD700" />
                <stop offset="60%"  stopColor="#FF8C00" />
                <stop offset="80%"  stopColor="#FF8C00" />
                <stop offset="80%"  stopColor="#FF4444" />
                <stop offset="100%" stopColor="#FF4444" />
              </linearGradient>
              <linearGradient id="tacoFillGradient" gradientUnits="userSpaceOnUse" x1="0" y1="5" x2="0" y2="283">
                <stop offset="0%"   stopColor="#008000" stopOpacity={0.15} />
                <stop offset="20%"  stopColor="#32CD32" stopOpacity={0.12} />
                <stop offset="40%"  stopColor="#FFD700" stopOpacity={0.08} />
                <stop offset="60%"  stopColor="#FF8C00" stopOpacity={0.06} />
                <stop offset="80%"  stopColor="#FF4444" stopOpacity={0.04} />
                <stop offset="100%" stopColor="#FF4444" stopOpacity={0}    />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />

            <XAxis
              dataKey="label"
              tick={{ fill: "#6B7280", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              yAxisId="left"
              domain={[0, 100]}
              tick={{ fill: "#6B7280", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={35}
            />
            {showRightAxis && (
              <YAxis
                yAxisId="right"
                orientation="right"
                domain={[pctMin, pctMax]}
                tick={{ fill: "#6B7280", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v > 0 ? "+" : ""}${v}%`}
                width={50}
              />
            )}

            <Tooltip
              contentStyle={{
                backgroundColor: "#111827",
                border: "1px solid #1F2937",
                borderRadius: 10,
                padding: "8px 12px",
              }}
              labelStyle={{ color: "#9CA3AF", fontSize: 12, marginBottom: 4 }}
              itemStyle={{ color: "#F9FAFB", fontSize: 12 }}
              formatter={(value, name) => {
                const v = Number(value);
                if (name === "tacoIndex") return [v, "TACO Index"];
                if (name === "btcPct") return [`${v > 0 ? "+" : ""}${v}%`, "BTC"];
                if (name === "spxPct") return [`${v > 0 ? "+" : ""}${v}%`, "S&P 500"];
                if (name === "goldPct") return [`${v > 0 ? "+" : ""}${v}%`, "Gold"];
                return [v, String(name)];
              }}
            />

            <ReferenceLine
              yAxisId="left"
              y={50}
              stroke="#374151"
              strokeDasharray="4 4"
            />
            {showRightAxis && (
              <ReferenceLine
                yAxisId="right"
                y={0}
                stroke="#374151"
                strokeDasharray="4 4"
              />
            )}

            <Area
              yAxisId="left"
              type="monotone"
              dataKey="tacoIndex"
              stroke="url(#tacoStrokeGradient)"
              fill="url(#tacoFillGradient)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#FFD700" }}
              connectNulls
            />

            {ASSET_CONFIG.map(({ key, color }) =>
              assets[key] ? (
                <Line
                  key={key}
                  yAxisId="right"
                  type="monotone"
                  dataKey={`${key}Pct`}
                  stroke={color}
                  strokeWidth={1.5}
                  strokeDasharray="5 3"
                  dot={false}
                  activeDot={{ r: 3, fill: color }}
                  connectNulls
                />
              ) : null
            )}
          </ComposedChart>
        </ResponsiveContainer>
      )}

      {/* Legend */}
      <div className="flex gap-4 mt-3 flex-wrap justify-end">
        <div className="flex items-center gap-1.5">
          <div
            className="w-4 h-0.5 rounded"
            style={{
              background: "linear-gradient(to right, #FF4444, #FF8C00, #FFD700, #32CD32, #008000)",
            }}
          />
          <span className="text-xs text-muted-foreground">TACO Index (0–100)</span>
        </div>
        {ASSET_CONFIG.filter((a) => assets[a.key]).map(({ key, label, color }) => (
          <div key={key} className="flex items-center gap-1.5">
            <div
              className="w-4 h-0.5"
              style={{
                backgroundImage: `repeating-linear-gradient(to right, ${color} 0, ${color} 5px, transparent 5px, transparent 8px)`,
              }}
            />
            <span className="text-xs text-muted-foreground">{label} (% change)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
