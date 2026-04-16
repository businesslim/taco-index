"use client";

import { useState, useEffect, useRef } from "react";
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
  TweetWithScore,
  fetchIndexHistory,
  fetchAssetHistory,
  fetchNotableTweets,
} from "@/lib/api";

type Range = "1d" | "7d" | "30d";
type Granularity = "hour" | "day";

interface ChartPoint {
  key: string;
  label: string;
  tacoIndex: number;
  btcPct?: number;
  spxPct?: number;
  goldPct?: number;
  notableTweets?: TweetWithScore[];
}

interface HoveredBucket {
  tweets: TweetWithScore[];
  cx: number;
  cy: number;
}

function parseDate(str: string): Date | null {
  const normalized = str
    .replace(/(\.\d{3})\d+/, "$1")
    .replace(/\+00:00$/, "Z");
  const dt = new Date(normalized);
  return isNaN(dt.getTime()) ? null : dt;
}

function aggregateTaco(
  data: IndexHistoryPoint[],
  by: Granularity
): { key: string; value: number }[] {
  const buckets = new Map<string, number[]>();
  for (const d of data) {
    const dt = parseDate(d.calculated_at);
    if (!dt) continue;
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
    const dt = parseDate(d.t);
    if (!dt) continue;
    const key =
      by === "hour"
        ? dt.toISOString().slice(0, 13)
        : dt.toISOString().slice(0, 10);
    map.set(key, d.price);
  }
  return map;
}

function buildTweetBuckets(
  tweets: TweetWithScore[],
  by: Granularity
): Map<string, TweetWithScore[]> {
  const map = new Map<string, TweetWithScore[]>();
  for (const t of tweets) {
    const dt = parseDate(t.posted_at);
    if (!dt) continue;
    const key =
      by === "hour"
        ? dt.toISOString().slice(0, 13)
        : dt.toISOString().slice(0, 10);
    const existing = map.get(key) ?? [];
    existing.push(t);
    map.set(key, existing);
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

function formatCardDate(isoStr: string): string {
  const dt = parseDate(isoStr);
  if (!dt) return "";
  return dt.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  }) + " UTC";
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
  const [notableTweets, setNotableTweets] = useState<TweetWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [hovered, setHovered] = useState<HoveredBucket | null>(null);
  const hideTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchIndexHistory(range),
      fetchAssetHistory(range),
      fetchNotableTweets(range),
    ])
      .then(([idx, asset, notable]) => {
        setIndexData(idx);
        setAssetData(asset);
        setNotableTweets(notable);
      })
      .catch((err) => {
        console.error("IndexHistoryChart fetch failed:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [range]);

  const showCard = (tweets: TweetWithScore[], cx: number, cy: number) => {
    if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
    // fixed 포지셔닝을 위해 viewport 기준 좌표로 변환
    const rect = chartRef.current?.getBoundingClientRect();
    const screenX = (rect?.left ?? 0) + cx;
    const screenY = (rect?.top ?? 0) + cy;
    setHovered({ tweets, cx: screenX, cy: screenY });
  };

  const scheduleHide = () => {
    hideTimeoutRef.current = setTimeout(() => setHovered(null), 150);
  };

  const by: Granularity = range === "1d" ? "hour" : "day";
  const tacoAgg = aggregateTaco(indexData, by);
  const keys = tacoAgg.map((d) => d.key);

  const btcPct = normalizeToPercent(buildPriceMap(assetData.btc, by), keys);
  const spxPct = normalizeToPercent(buildPriceMap(assetData.spx, by), keys);
  const goldPct = normalizeToPercent(buildPriceMap(assetData.gold, by), keys);
  const tweetBuckets = buildTweetBuckets(notableTweets, by);

  const chartData: ChartPoint[] = tacoAgg.map((d) => ({
    key: d.key,
    label: formatLabel(d.key, by),
    tacoIndex: d.value,
    btcPct: btcPct.get(d.key),
    spxPct: spxPct.get(d.key),
    goldPct: goldPct.get(d.key),
    notableTweets: tweetBuckets.get(d.key),
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
  const rawAbsMax = allPcts.length > 0
    ? Math.max(Math.abs(Math.min(...allPcts)), Math.abs(Math.max(...allPcts)))
    : 10;
  const pctAbsMax = Math.ceil(rawAbsMax + pctPad);
  const pctMin = -pctAbsMax;
  const pctMax = pctAbsMax;

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
            <button
              key={opt.value}
              onClick={() => setRange(opt.value)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                range === opt.value
                  ? "bg-foreground/10 text-foreground ring-1 ring-foreground/20"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {opt.label}
            </button>
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
        <div ref={chartRef} className="relative" style={{ outline: "none" }}>
          <ResponsiveContainer width="100%" height={288}>
            <ComposedChart
              data={chartData}
              margin={{ top: 8, right: 0, left: 0, bottom: 5 }}
            >
              <defs>
                {/*
                  gradientUnits="userSpaceOnUse": SVG 좌표로 색 경계 지정
                  chart height=288, margin.top=8, margin.bottom=5, XAxis height=30
                  → 실제 데이터 플로팅 영역: y=8 ~ y=253 (288-5-30)
                  value=100→y=8, 80→y=57, 60→y=106, 40→y=155, 20→y=204, 0→y=253
                  → offset 20%=value80, 40%=value60, 60%=value40, 80%=value20
                */}
                <linearGradient id="tacoStrokeGradient" gradientUnits="userSpaceOnUse" x1="0" y1="8" x2="0" y2="253">
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
                <linearGradient id="tacoFillGradient" gradientUnits="userSpaceOnUse" x1="0" y1="8" x2="0" y2="253">
                  <stop offset="0%"   stopColor="#008000" stopOpacity={0.15} />
                  <stop offset="20%"  stopColor="#32CD32" stopOpacity={0.12} />
                  <stop offset="40%"  stopColor="#FFD700" stopOpacity={0.08} />
                  <stop offset="60%"  stopColor="#FF8C00" stopOpacity={0.06} />
                  <stop offset="80%"  stopColor="#FF4444" stopOpacity={0.04} />
                  <stop offset="100%" stopColor="#FF4444" stopOpacity={0}    />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#1a2436" />

              <XAxis
                dataKey="label"
                tick={{ fill: "#6b7fa3", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="left"
                domain={[0, 100]}
                tick={{ fill: "#6b7fa3", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={36}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                domain={showRightAxis ? [pctMin, pctMax] : [0, 100]}
                tick={showRightAxis ? { fill: "#6b7fa3", fontSize: 11 } : false}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v > 0 ? "+" : ""}${v}%`}
                width={52}
              />

              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1320",
                  border: "1px solid #1a2436",
                  borderRadius: 6,
                  padding: "8px 12px",
                }}
                labelStyle={{ color: "#6b7fa3", fontSize: 12, marginBottom: 4 }}
                itemStyle={{ color: "#e8edf5", fontSize: 12 }}
                formatter={(value, name) => {
                  const v = Number(value);
                  if (name === "tacoIndex") return [v, "TACO Index"];
                  if (name === "btcPct") return [`${v > 0 ? "+" : ""}${v}%`, "BTC"];
                  if (name === "spxPct") return [`${v > 0 ? "+" : ""}${v}%`, "S&P 500"];
                  if (name === "goldPct") return [`${v > 0 ? "+" : ""}${v}%`, "Gold"];
                  return [v, String(name)];
                }}
              />

              {/* 기준선 통합: TACO=50 이자 자산 0% 기준선 (대칭 도메인으로 동일 높이) */}
              <ReferenceLine
                yAxisId="left"
                y={50}
                stroke="#2a3a52"
                strokeDasharray="4 4"
              />

              <Area
                yAxisId="left"
                type="monotone"
                dataKey="tacoIndex"
                stroke="url(#tacoStrokeGradient)"
                fill="url(#tacoFillGradient)"
                strokeWidth={2}
                activeDot={{ r: 4, fill: "#FFD700" }}
                connectNulls
                dot={(props: {
                  cx?: number;
                  cy?: number;
                  index?: number;
                }) => {
                  const { cx, cy, index } = props;
                  if (cx === undefined || cy === undefined || index === undefined) {
                    return <g key="dot-empty" />;
                  }
                  const point = chartData[index];
                  if (!point?.notableTweets?.length) {
                    return <g key={`dot-${index}`} />;
                  }
                  const tweets = point.notableTweets;
                  const extreme = tweets.reduce((a, b) =>
                    Math.abs(a.final_score - 50) > Math.abs(b.final_score - 50) ? a : b
                  );
                  const color = extreme.band_color;
                  return (
                    <g
                      key={`dot-notable-${index}`}
                      style={{ cursor: "pointer" }}
                      onMouseEnter={() => showCard(tweets, cx, cy)}
                      onMouseLeave={scheduleHide}
                    >
                      <circle cx={cx} cy={cy} r={10} fill={color} fillOpacity={0.15} />
                      <circle cx={cx} cy={cy} r={5} fill={color} stroke="#0d1320" strokeWidth={1.5} />
                      {tweets.length > 1 && (
                        <text
                          x={cx + 8}
                          y={cy - 8}
                          fontSize={9}
                          fill={color}
                          fontWeight="bold"
                          style={{ pointerEvents: "none" }}
                        >
                          {tweets.length}
                        </text>
                      )}
                    </g>
                  );
                }}
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

          {/* Notable tweet floating card — fixed 포지셔닝으로 부모 overflow 영향 없음 */}
          {hovered && (
            <div
              className="pointer-events-auto"
              style={{
                position: "fixed",
                left: hovered.cx,
                top: hovered.cy < 200 ? hovered.cy + 14 : hovered.cy - 14,
                transform: hovered.cy < 200
                  ? "translateX(-50%)"
                  : "translate(-50%, -100%)",
                zIndex: 9999,
              }}
              onMouseEnter={() => {
                if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
              }}
              onMouseLeave={scheduleHide}
            >
              <div
                className="rounded-lg shadow-xl p-3 flex flex-col gap-2"
                style={{
                  backgroundColor: "#0d1320",
                  border: "1px solid #1a2436",
                  minWidth: "240px",
                  maxWidth: "320px",
                  maxHeight: "320px",
                  overflowY: "auto",
                }}
              >
                {hovered.tweets.map((tweet, i) => (
                  <a
                    key={tweet.tweet_id}
                    href={`https://truthsocial.com/@realDonaldTrump/posts/${tweet.tweet_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex flex-col gap-1 group"
                    style={
                      i < hovered.tweets.length - 1
                        ? { paddingBottom: "10px", borderBottom: "1px solid #1a2436" }
                        : undefined
                    }
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className="shrink-0 text-xs font-bold font-mono px-1.5 py-0.5 rounded"
                        style={{
                          color: tweet.band_color,
                          backgroundColor: tweet.band_color + "22",
                          border: `1px solid ${tweet.band_color}44`,
                        }}
                      >
                        {tweet.final_score}
                      </span>
                      <span className="text-xs" style={{ color: "#6b7fa3" }}>
                        {formatCardDate(tweet.posted_at)}
                      </span>
                    </div>
                    <p
                      className="text-xs leading-relaxed group-hover:opacity-80 transition-opacity"
                      style={{ color: "#e8edf5" }}
                    >
                      {tweet.content}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
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
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-current" style={{ color: "#FFD700" }} />
          <span className="text-xs text-muted-foreground">Notable post (score ≤40 or ≥60)</span>
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
