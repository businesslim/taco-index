import { ImageResponse } from "next/og";

export const runtime = "edge";
export const revalidate = 300;
export const alt = "TACO Index — Real-time market sentiment from Trump's Truth Social";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const BAND_META: Record<
  string,
  { label: string; color: string; emoji: string }
> = {
  "Taco de Habanero": { label: "Extreme Bearish", color: "#ef4444", emoji: "🌶️" },
  "Taco de Chorizo":  { label: "Bearish",         color: "#f97316", emoji: "🥩" },
  "Cooking...":       { label: "Neutral",         color: "#eab308", emoji: "⏳" },
  "Taco de Frijoles": { label: "Bullish",         color: "#84cc16", emoji: "🌮" },
  "Taco de CHICKEN":  { label: "Extreme Bullish", color: "#22c55e", emoji: "🏆" },
};

export default async function OpengraphImage() {
  const apiBase =
    process.env.NEXT_PUBLIC_API_URL ?? "https://tacoindex.up.railway.app";

  let indexValue: number | null = null;
  let bandLabel = "Cooking...";
  try {
    const res = await fetch(`${apiBase}/api/index/current`, {
      next: { revalidate: 300 },
    });
    if (res.ok) {
      const data = await res.json();
      if (typeof data.index_value === "number") indexValue = data.index_value;
      if (typeof data.band_label === "string") bandLabel = data.band_label;
    }
  } catch {
    // fall back to defaults
  }

  const meta =
    BAND_META[bandLabel] ?? {
      label: bandLabel,
      color: "#94a3b8",
      emoji: "🌮",
    };

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background:
            "radial-gradient(ellipse at top left, #1e293b 0%, #0a0a0f 60%)",
          padding: 80,
          fontFamily: "sans-serif",
          color: "#fafafa",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 18,
          }}
        >
          <span style={{ fontSize: 56 }}>🌮</span>
          <span
            style={{
              fontSize: 34,
              color: "#94a3b8",
              letterSpacing: 6,
              fontWeight: 700,
            }}
          >
            TACO INDEX
          </span>
        </div>

        <div
          style={{
            display: "flex",
            flex: 1,
            alignItems: "center",
            justifyContent: "space-between",
            marginTop: 30,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div
              style={{
                fontSize: 280,
                fontWeight: 800,
                lineHeight: 1,
                color: meta.color,
                letterSpacing: -8,
              }}
            >
              {indexValue ?? "—"}
            </div>
            <div
              style={{
                fontSize: 56,
                fontWeight: 700,
                color: "#cbd5e1",
                marginTop: 12,
              }}
            >
              {meta.label}
            </div>
          </div>
          <div style={{ fontSize: 240, lineHeight: 1 }}>{meta.emoji}</div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: 30,
          }}
        >
          <span style={{ fontSize: 24, color: "#64748b" }}>
            Real-time market sentiment from Trump&apos;s Truth Social
          </span>
          <span
            style={{
              fontSize: 28,
              color: "#f59e0b",
              fontWeight: 700,
            }}
          >
            taco-index.com
          </span>
        </div>
      </div>
    ),
    { ...size },
  );
}
