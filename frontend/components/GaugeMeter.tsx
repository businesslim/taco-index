"use client";

interface GaugeMeterProps {
  value: number;    // 0~100
  label: string;    // e.g. "Bullish"
  color: string;    // HEX color
}

export default function GaugeMeter({ value, label, color }: GaugeMeterProps) {
  const clampedValue = Math.max(0, Math.min(100, value));
  // 0~100 → -90° ~ +90° (180° total arc)
  const angle = (clampedValue / 100) * 180 - 90;
  const needleRad = (angle * Math.PI) / 180;
  const needleX = 100 + 70 * Math.cos(needleRad);
  const needleY = 100 + 70 * Math.sin(needleRad);

  const segments = [
    { color: "#FF4444" }, // Extreme Bearish
    { color: "#FF8C00" }, // Bearish
    { color: "#FFD700" }, // Neutral
    { color: "#32CD32" }, // Bullish
    { color: "#008000" }, // Extreme Bullish
  ];

  function polarToCartesian(cx: number, cy: number, r: number, deg: number) {
    const rad = ((deg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  function describeArc(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
    const start = polarToCartesian(cx, cy, r, endDeg);
    const end = polarToCartesian(cx, cy, r, startDeg);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
  }

  let cumulative = 0;
  return (
    <div className="flex flex-col items-center gap-4">
      <svg viewBox="0 0 200 120" className="w-72 h-44">
        {segments.map((seg, i) => {
          const startDeg = 180 + cumulative * 1.8;
          cumulative += 20;
          const endDeg = 180 + cumulative * 1.8;
          return (
            <path
              key={i}
              d={describeArc(100, 100, 75, startDeg, endDeg)}
              fill="none"
              stroke={seg.color}
              strokeWidth="18"
            />
          );
        })}
        <line
          x1="100"
          y1="100"
          x2={needleX}
          y2={needleY}
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="100" cy="100" r="5" fill="white" />
      </svg>
      <div className="text-center">
        <p className="text-6xl font-bold" style={{ color }}>
          {clampedValue}
        </p>
        <p className="text-xl mt-1 font-medium" style={{ color }}>
          {label}
        </p>
      </div>
    </div>
  );
}
