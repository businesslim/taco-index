"use client";

import TacoIcon from "@/components/TacoIcon";

interface GaugeMeterProps {
  value: number; // 0~100
  label: string;
  color: string;
  compact?: boolean;
}

export default function GaugeMeter({ value, label, color, compact = false }: GaugeMeterProps) {
  const v = Math.max(0, Math.min(100, value));
  const cx = 100;
  const cy = 100;
  const r = 70;
  const sw = 18;

  // 표준 수학 좌표 (0°=오른쪽, 90°=위) → SVG 좌표 변환
  // 0%  → 180° → 왼쪽 끝 (Extreme Bearish, 빨강)
  // 50% →  90° → 정중앙 위 (Neutral, 노랑)
  // 100%→   0° → 오른쪽 끝 (Extreme Bullish, 초록)
  function toPoint(pct: number) {
    const theta = Math.PI * (1 - pct / 100);
    return {
      x: cx + r * Math.cos(theta),
      y: cy - r * Math.sin(theta),
    };
  }

  // 좌→우: 빨강 → 주황 → 노랑 → 연두 → 진초록
  const segments = [
    "#FF4444", // 0~20  Extreme Bearish
    "#FF8C00", // 20~40 Bearish
    "#FFD700", // 40~60 Neutral
    "#32CD32", // 60~80 Bullish
    "#008000", // 80~100 Extreme Bullish
  ];

  const paths = segments.map((segColor, i) => {
    const start = toPoint(i * 20);
    const end = toPoint((i + 1) * 20);
    return {
      segColor,
      d: `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${r} ${r} 0 0 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`,
    };
  });

  // 바늘: 0=왼쪽, 50=정중앙(위), 100=오른쪽
  const needleAngle = Math.PI * (1 - v / 100);
  const needleLen = r - sw / 2 - 4;
  const needleX = cx + needleLen * Math.cos(needleAngle);
  const needleY = cy - needleLen * Math.sin(needleAngle);

  return (
    <div className="flex flex-col items-center gap-2">
      <svg
        viewBox="0 0 200 115"
        className={compact ? "w-48 h-28" : "w-72 h-44"}
      >
        {paths.map((seg, i) => (
          <path
            key={i}
            d={seg.d}
            fill="none"
            stroke={seg.segColor}
            strokeWidth={sw}
            strokeLinecap="butt"
          />
        ))}
        <line
          x1={cx}
          y1={cy}
          x2={needleX.toFixed(2)}
          y2={needleY.toFixed(2)}
          stroke="#F59E0B"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="5" fill="#F59E0B" />
      </svg>
      <div className="text-center flex flex-col items-center gap-1">
        <TacoIcon bandLabel={label} size={compact ? 48 : 80} />
        <p className={compact ? "text-4xl font-bold font-mono" : "text-6xl font-bold font-mono"} style={{ color }}>
          {v}
        </p>
        <p className={compact ? "text-base font-medium" : "text-xl mt-1 font-medium"} style={{ color }}>
          {label}
        </p>
      </div>
    </div>
  );
}
