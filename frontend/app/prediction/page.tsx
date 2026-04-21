"use client";

import { useSession, signIn } from "next-auth/react";
import { useEffect, useState } from "react";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  fetchPredictionStats,
  fetchMyPredictions,
  submitPrediction,
  PredictionStats,
  MyPredictions,
} from "@/lib/api";

const ASSETS = ["BTC", "SPX", "GOLD"];
const TIMEFRAMES = [
  { value: "daily", label: "Tomorrow" },
  { value: "weekly", label: "Next Week" },
  { value: "monthly", label: "Next Month" },
];

const ASSET_LABELS: Record<string, string> = {
  BTC: "Bitcoin",
  SPX: "S&P 500",
  GOLD: "Gold",
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

export default function PredictionPage() {
  const { data: session } = useSession();
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [myData, setMyData] = useState<MyPredictions | null>(null);
  const [selectedAsset, setSelectedAsset] = useState("BTC");
  const [selectedTimeframe, setSelectedTimeframe] = useState("daily");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchPredictionStats().then(setStats);
  }, []);

  useEffect(() => {
    if (session?.user?.email) {
      fetchMyPredictions(session.user.email).then(setMyData);
    }
  }, [session, success]);

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
                <p className="text-xs font-medium text-slate-300">{ASSET_LABELS[asset]}</p>
                {TIMEFRAMES.map(({ value, label }) => {
                  const c = stats?.consensus?.[asset]?.[value];
                  const total = c?.total ?? 0;
                  const bullPct = total > 0 ? Math.round((c!.bullish / total) * 100) : 50;
                  const bearPct = 100 - bullPct;
                  return (
                    <div key={value} className="flex flex-col gap-0.5">
                      <p className="text-xs text-slate-500">{label}</p>
                      <div className="flex rounded overflow-hidden h-2 bg-slate-800">
                        <div className="bg-green-500" style={{ width: `${bullPct}%` }} />
                        <div className="bg-red-500" style={{ width: `${bearPct}%` }} />
                      </div>
                      <p className="text-xs text-slate-500">
                        📈 {bullPct}% · 📉 {bearPct}%
                        {total > 0 && <span className="ml-1 text-slate-600">({total})</span>}
                      </p>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 예측 폼 또는 로그인 유도 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Make a Prediction</CardTitle>
        </CardHeader>
        <CardContent>
          {!session ? (
            <div className="flex flex-col items-center gap-3 py-4">
              <p className="text-sm text-slate-400">Sign in to submit your prediction</p>
              <button
                onClick={() => signIn("google")}
                className="flex items-center gap-2 px-4 py-2 rounded text-sm font-medium"
                style={{ backgroundColor: "#3B82F622", color: "#93C5FD", border: "1px solid #3B82F644" }}
              >
                Sign in with Google
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {/* Asset 선택 */}
              <div className="flex gap-2">
                {ASSETS.map((a) => (
                  <button
                    key={a}
                    onClick={() => setSelectedAsset(a)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      selectedAsset === a
                        ? "bg-amber-500 text-black"
                        : "bg-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {a}
                  </button>
                ))}
              </div>

              {/* Timeframe 선택 */}
              <div className="flex gap-2">
                {TIMEFRAMES.map(({ value, label }) => (
                  <button
                    key={value}
                    onClick={() => setSelectedTimeframe(value)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      selectedTimeframe === value
                        ? "bg-amber-500 text-black"
                        : "bg-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {/* 방향 선택 */}
              <div className="flex gap-3">
                <button
                  onClick={() => handlePredict("bullish")}
                  disabled={submitting}
                  className="flex-1 py-3 rounded font-medium text-sm bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 transition-colors disabled:opacity-50"
                >
                  📈 Bullish
                </button>
                <button
                  onClick={() => handlePredict("bearish")}
                  disabled={submitting}
                  className="flex-1 py-3 rounded font-medium text-sm bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-colors disabled:opacity-50"
                >
                  📉 Bearish
                </button>
              </div>

              {error && <p className="text-xs text-red-400">{error}</p>}
              {success && <p className="text-xs text-green-400">Prediction submitted!</p>}
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
                <span>Total: <strong className="text-slate-200">{myData.stats.total}</strong></span>
                <span>Correct: <strong className="text-green-400">{myData.stats.correct}</strong></span>
                <span>Accuracy: <strong className="text-amber-400">{myData.stats.accuracy}%</strong></span>
              </div>
              <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
                {myData.predictions.length === 0 ? (
                  <p className="text-xs text-slate-500">No predictions yet.</p>
                ) : (
                  myData.predictions.map((p) => (
                    <div key={p.id} className="flex justify-between items-center text-xs py-1.5 border-b border-slate-800">
                      <span className="text-slate-300">
                        {p.asset} · {p.timeframe} · {p.direction === "bullish" ? "📈" : "📉"}
                      </span>
                      <span className={RESULT_STYLE[p.result]}>{RESULT_LABEL[p.result]}</span>
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
              <p className="text-xs text-slate-500">Not enough data yet. (min. 5 predictions)</p>
            ) : (
              <div className="flex flex-col gap-2">
                {stats.leaderboard.map((u, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="text-slate-500 w-4">{i + 1}</span>
                    {u.image && (
                      <Image src={u.image} alt={u.name} width={20} height={20} className="rounded-full" />
                    )}
                    <span className="text-slate-300 flex-1 truncate">{u.name}</span>
                    <span className="text-amber-400 font-medium">{u.accuracy}%</span>
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
