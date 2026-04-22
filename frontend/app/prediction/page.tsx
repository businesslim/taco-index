"use client";

import { useSession, signIn } from "next-auth/react";
import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  fetchPredictionStats,
  fetchMyPredictions,
  submitPrediction,
  fetchAssetHistory,
  fetchCurrentIndex,
  PredictionStats,
  MyPredictions,
  AssetHistory,
  CurrentIndex,
} from "@/lib/api";

const ASSETS = ["BTC", "SPX", "GOLD"] as const;
type Asset = (typeof ASSETS)[number];

const TIMEFRAMES = [
  { value: "daily", label: "Tomorrow", days: 1 },
  { value: "weekly", label: "Next Week", days: 7 },
  { value: "monthly", label: "Next Month", days: 30 },
] as const;

const ASSET_META: Record<
  Asset,
  {
    label: string;
    icon: string;
    accent: string;
    historyKey: keyof AssetHistory;
    formatPrice: (n: number) => string;
  }
> = {
  BTC: {
    label: "Bitcoin",
    icon: "₿",
    accent: "#F7931A",
    historyKey: "btc",
    formatPrice: (n) => `$${Math.round(n).toLocaleString()}`,
  },
  SPX: {
    label: "S&P 500",
    icon: "§",
    accent: "#3B82F6",
    historyKey: "spx",
    formatPrice: (n) =>
      n.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }),
  },
  GOLD: {
    label: "Gold",
    icon: "Au",
    accent: "#EAB308",
    historyKey: "gold",
    formatPrice: (n) => `$${n.toFixed(2)}`,
  },
};

const RESULT_STYLE: Record<string, string> = {
  correct: "text-green-400",
  incorrect: "text-red-400",
  pending: "text-slate-400",
};

const RESULT_LABEL: Record<string, string> = {
  correct: "✓ Correct",
  incorrect: "✗ Incorrect",
  pending: "⏳ Pending",
};

function Sparkline({
  points,
  color,
  width = 96,
  height = 32,
}: {
  points: number[];
  color: string;
  width?: number;
  height?: number;
}) {
  if (points.length < 2) {
    return <div style={{ width, height }} className="opacity-30" />;
  }
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const coords = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * width;
      const y = height - ((p - min) / range) * height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
  const areaCoords = `0,${height} ${coords} ${width},${height}`;
  const gradId = `spark-grad-${color.replace("#", "")}`;
  return (
    <svg
      width={width}
      height={height}
      className="overflow-visible"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon fill={`url(#${gradId})`} points={areaCoords} />
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
        points={coords}
      />
    </svg>
  );
}

function formatEvaluateDate(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function PredictionPage() {
  const { data: session } = useSession();
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [myData, setMyData] = useState<MyPredictions | null>(null);
  const [history, setHistory] = useState<AssetHistory | null>(null);
  const [tacoIndex, setTacoIndex] = useState<CurrentIndex | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset>("BTC");
  const [selectedTimeframe, setSelectedTimeframe] = useState("daily");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchPredictionStats().then(setStats);
    fetchAssetHistory("7d").then(setHistory);
    fetchCurrentIndex().then(setTacoIndex).catch(() => {});
  }, []);

  useEffect(() => {
    if (session?.user?.email) {
      fetchMyPredictions(session.user.email).then(setMyData);
    }
  }, [session, success]);

  const assetSummaries = useMemo(() => {
    const out: Record<
      Asset,
      { current: number | null; change: number | null; series: number[] }
    > = {
      BTC: { current: null, change: null, series: [] },
      SPX: { current: null, change: null, series: [] },
      GOLD: { current: null, change: null, series: [] },
    };
    if (!history) return out;
    for (const asset of ASSETS) {
      const series = (history[ASSET_META[asset].historyKey] ?? []).map(
        (p) => p.price
      );
      if (series.length === 0) continue;
      const first = series[0];
      const last = series[series.length - 1];
      out[asset] = {
        current: last,
        change: first > 0 ? ((last - first) / first) * 100 : 0,
        series,
      };
    }
    return out;
  }, [history]);

  const activeSummary = assetSummaries[selectedAsset];
  const activeMeta = ASSET_META[selectedAsset];
  const activeTimeframe = TIMEFRAMES.find((t) => t.value === selectedTimeframe)!;

  const indexBandTone = useMemo(() => {
    const v = tacoIndex?.index_value ?? 50;
    if (v >= 70) return { tone: "bullish" as const, label: "tilts bullish" };
    if (v <= 30) return { tone: "bearish" as const, label: "tilts bearish" };
    return { tone: "neutral" as const, label: "is neutral" };
  }, [tacoIndex]);

  async function handlePredict(direction: "bullish" | "bearish") {
    if (!session?.user?.email) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitPrediction({
        email: session.user.email,
        name: session.user.name ?? undefined,
        image: session.user.image ?? undefined,
        asset: selectedAsset,
        timeframe: selectedTimeframe,
        direction,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      fetchPredictionStats().then(setStats);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit prediction");
    } finally {
      setSubmitting(false);
    }
  }

  const priceText =
    activeSummary.current !== null
      ? activeMeta.formatPrice(activeSummary.current)
      : "—";
  const changeText =
    activeSummary.change !== null
      ? `${activeSummary.change >= 0 ? "+" : ""}${activeSummary.change.toFixed(
          2
        )}%`
      : "—";
  const changePositive = (activeSummary.change ?? 0) >= 0;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-1.5">
        <h2 className="text-lg font-semibold text-foreground">TACO Prediction</h2>
        <p className="text-muted-foreground text-sm leading-relaxed">
          Predict where BTC, S&P 500, and Gold will move — and see how you stack up against the community.
        </p>
      </div>

      {/* 커뮤니티 컨센서스 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Community Consensus</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {ASSETS.map((asset) => (
              <div key={asset} className="flex flex-col gap-2">
                <p className="text-xs font-medium text-slate-300">
                  {ASSET_META[asset].label}
                </p>
                {TIMEFRAMES.map(({ value, label }) => {
                  const c = stats?.consensus?.[asset]?.[value];
                  const total = c?.total ?? 0;
                  const bullPct =
                    total > 0 ? Math.round((c!.bullish / total) * 100) : 50;
                  const bearPct = 100 - bullPct;
                  return (
                    <div key={value} className="flex flex-col gap-0.5">
                      <p className="text-xs text-slate-500">{label}</p>
                      <div className="flex rounded overflow-hidden h-2 bg-slate-800">
                        <div
                          className="bg-green-500"
                          style={{ width: `${bullPct}%` }}
                        />
                        <div
                          className="bg-red-500"
                          style={{ width: `${bearPct}%` }}
                        />
                      </div>
                      <p className="text-xs text-slate-500">
                        📈 {bullPct}% · 📉 {bearPct}%
                        {total > 0 && (
                          <span className="ml-1 text-slate-600">({total})</span>
                        )}
                      </p>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 예측 폼 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Make a Prediction</CardTitle>
        </CardHeader>
        <CardContent>
          {!session ? (
            <div className="flex flex-col items-center gap-3 py-4">
              <p className="text-sm text-slate-400">
                Sign in to submit your prediction
              </p>
              <button
                onClick={() => signIn("google")}
                className="flex items-center gap-2 px-4 py-2 rounded text-sm font-medium"
                style={{
                  backgroundColor: "#3B82F622",
                  color: "#93C5FD",
                  border: "1px solid #3B82F644",
                }}
              >
                Sign in with Google
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-5">
              {/* Asset 탭: 아이콘 + 라벨 + 가격 */}
              <div className="grid grid-cols-3 gap-2">
                {ASSETS.map((a) => {
                  const meta = ASSET_META[a];
                  const sum = assetSummaries[a];
                  const isActive = selectedAsset === a;
                  return (
                    <button
                      key={a}
                      onClick={() => setSelectedAsset(a)}
                      className="flex flex-col items-start gap-1 rounded-lg border px-3 py-2.5 text-left transition-all"
                      style={{
                        backgroundColor: isActive
                          ? `${meta.accent}1A`
                          : "rgba(30,41,59,0.4)",
                        borderColor: isActive
                          ? `${meta.accent}66`
                          : "rgba(51,65,85,0.6)",
                        boxShadow: isActive
                          ? `0 0 0 1px ${meta.accent}33`
                          : undefined,
                      }}
                    >
                      <div className="flex items-center gap-1.5">
                        <span
                          className="flex items-center justify-center w-5 h-5 rounded text-[11px] font-bold"
                          style={{
                            backgroundColor: `${meta.accent}33`,
                            color: meta.accent,
                          }}
                        >
                          {meta.icon}
                        </span>
                        <span
                          className="text-xs font-semibold"
                          style={{
                            color: isActive ? meta.accent : "#CBD5E1",
                          }}
                        >
                          {a}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 truncate w-full">
                        {sum.current !== null
                          ? meta.formatPrice(sum.current)
                          : meta.label}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Selected Asset Hero */}
              <div
                className="flex items-center justify-between gap-4 rounded-lg border px-4 py-3"
                style={{
                  backgroundColor: `${activeMeta.accent}0D`,
                  borderColor: `${activeMeta.accent}33`,
                }}
              >
                <div className="flex flex-col gap-0.5 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className="flex items-center justify-center w-6 h-6 rounded text-xs font-bold"
                      style={{
                        backgroundColor: `${activeMeta.accent}33`,
                        color: activeMeta.accent,
                      }}
                    >
                      {activeMeta.icon}
                    </span>
                    <span className="text-xs text-slate-400">
                      {activeMeta.label}
                    </span>
                  </div>
                  <span className="text-2xl font-bold text-slate-100 tracking-tight">
                    {priceText}
                  </span>
                  <span
                    className={`text-xs font-medium ${
                      changePositive ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {changeText}{" "}
                    <span className="text-slate-500 font-normal">· 7d</span>
                  </span>
                </div>
                <Sparkline
                  points={activeSummary.series}
                  color={changePositive ? "#22c55e" : "#ef4444"}
                  width={110}
                  height={40}
                />
              </div>

              {/* TACO Index 컨텍스트 */}
              {tacoIndex && (
                <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/40 rounded px-3 py-2">
                  <span className="text-base">🌮</span>
                  <span>
                    TACO Index is{" "}
                    <strong
                      className="text-slate-200"
                      style={{ color: tacoIndex.band_color }}
                    >
                      {tacoIndex.index_value} · {tacoIndex.band_label}
                    </strong>{" "}
                    — market sentiment {indexBandTone.label}.
                  </span>
                </div>
              )}

              {/* Timeframe 선택 */}
              <div className="flex flex-col gap-2">
                <p className="text-xs text-slate-400">
                  When should this play out?
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {TIMEFRAMES.map(({ value, label }) => (
                    <button
                      key={value}
                      onClick={() => setSelectedTimeframe(value)}
                      className={`py-2 rounded-lg text-xs font-medium transition-colors border ${
                        selectedTimeframe === value
                          ? "bg-amber-500/15 text-amber-300 border-amber-500/40"
                          : "bg-slate-800/40 text-slate-400 border-slate-700/50 hover:text-slate-200"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500">
                  Evaluates on or around{" "}
                  <span className="text-slate-400">
                    {formatEvaluateDate(activeTimeframe.days)}
                  </span>
                  .
                </p>
              </div>

              {/* 방향 선택 */}
              <div className="flex flex-col gap-2">
                <p className="text-xs text-slate-400">Your call?</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => handlePredict("bullish")}
                    disabled={submitting}
                    className="flex-1 py-3.5 rounded-lg font-semibold text-sm bg-green-500/15 text-green-400 border border-green-500/40 hover:bg-green-500/25 hover:border-green-500/60 transition-colors disabled:opacity-50 flex flex-col gap-0.5 items-center"
                  >
                    <span>📈 Bullish</span>
                    <span className="text-[10px] text-green-500/70 font-normal">
                      price will rise
                    </span>
                  </button>
                  <button
                    onClick={() => handlePredict("bearish")}
                    disabled={submitting}
                    className="flex-1 py-3.5 rounded-lg font-semibold text-sm bg-red-500/15 text-red-400 border border-red-500/40 hover:bg-red-500/25 hover:border-red-500/60 transition-colors disabled:opacity-50 flex flex-col gap-0.5 items-center"
                  >
                    <span>📉 Bearish</span>
                    <span className="text-[10px] text-red-500/70 font-normal">
                      price will fall
                    </span>
                  </button>
                </div>
              </div>

              {error && <p className="text-xs text-red-400">{error}</p>}
              {success && (
                <p className="text-xs text-green-400">
                  Prediction locked in. See you on{" "}
                  {formatEvaluateDate(activeTimeframe.days)}.
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* 내 예측 히스토리 */}
        {session && myData && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">My Predictions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-4 text-xs text-slate-400">
                <span>
                  Total:{" "}
                  <strong className="text-slate-200">
                    {myData.stats.total}
                  </strong>
                </span>
                <span>
                  Correct:{" "}
                  <strong className="text-green-400">
                    {myData.stats.correct}
                  </strong>
                </span>
                <span>
                  Accuracy:{" "}
                  <strong className="text-amber-400">
                    {myData.stats.accuracy}%
                  </strong>
                </span>
              </div>
              <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
                {myData.predictions.length === 0 ? (
                  <p className="text-xs text-slate-500">No predictions yet.</p>
                ) : (
                  myData.predictions.map((p) => (
                    <div
                      key={p.id}
                      className="flex justify-between items-center text-xs py-1.5 border-b border-slate-800"
                    >
                      <span className="text-slate-300">
                        {p.asset} · {p.timeframe} ·{" "}
                        {p.direction === "bullish" ? "📈" : "📉"}
                      </span>
                      <span className={RESULT_STYLE[p.result]}>
                        {RESULT_LABEL[p.result]}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 리더보드 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Leaderboard</CardTitle>
          </CardHeader>
          <CardContent>
            {!stats?.leaderboard?.length ? (
              <p className="text-xs text-slate-500">
                Not enough data yet. (min. 5 predictions)
              </p>
            ) : (
              <div className="flex flex-col gap-2">
                {stats.leaderboard.map((u, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="text-slate-500 w-4">{i + 1}</span>
                    {u.image && (
                      <Image
                        src={u.image}
                        alt={u.name}
                        width={20}
                        height={20}
                        className="rounded-full"
                      />
                    )}
                    <span className="text-slate-300 flex-1 truncate">
                      {u.name}
                    </span>
                    <span className="text-amber-400 font-medium">
                      {u.accuracy}%
                    </span>
                    <span className="text-slate-500">({u.total})</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
