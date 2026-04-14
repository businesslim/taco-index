"use client";

const TACO_CONTENTS: Record<string, { label: string; content: React.ReactNode }> = {
  "Taco de Habanero": {
    label: "Taco de Habanero",
    content: (
      <>
        {/* Flames */}
        <path d="M 26 34 Q 29 20 34 30 Q 37 14 42 28 Q 46 18 50 32"
          stroke="#FF6600" strokeWidth="3" fill="none" strokeLinecap="round" />
        {/* Shell */}
        <path d="M 8 54 Q 40 12 72 54"
          stroke="#B22222" strokeWidth="11" fill="none" strokeLinecap="round" />
        {/* Filling */}
        <ellipse cx="40" cy="57" rx="26" ry="8" fill="#FF4500" />
        {/* Hot spots */}
        <circle cx="30" cy="57" r="2.5" fill="#FFD700" />
        <circle cx="40" cy="59" r="2.5" fill="#FFD700" />
        <circle cx="50" cy="57" r="2.5" fill="#FFD700" />
      </>
    ),
  },
  "Taco de Chorizo": {
    label: "Taco de Chorizo",
    content: (
      <>
        {/* Shell */}
        <path d="M 8 54 Q 40 12 72 54"
          stroke="#7B3F00" strokeWidth="11" fill="none" strokeLinecap="round" />
        {/* Filling */}
        <ellipse cx="40" cy="57" rx="26" ry="8" fill="#CC4400" />
        {/* Chorizo slices */}
        <circle cx="27" cy="56" r="3.5" fill="#8B0000" />
        <circle cx="37" cy="59" r="3.5" fill="#8B0000" />
        <circle cx="47" cy="58" r="3.5" fill="#8B0000" />
        <circle cx="56" cy="55" r="3" fill="#8B0000" />
      </>
    ),
  },
  "Cooking...": {
    label: "Cooking...",
    content: (
      <>
        {/* Shell (dashed = not yet done) */}
        <path d="M 8 54 Q 40 12 72 54"
          stroke="#777" strokeWidth="10" fill="none"
          strokeLinecap="round" strokeDasharray="9 5" />
        {/* Empty filling */}
        <ellipse cx="40" cy="57" rx="26" ry="8" fill="#444" />
        {/* Three dots */}
        <circle cx="28" cy="32" r="4.5" fill="#FFD700" />
        <circle cx="40" cy="28" r="4.5" fill="#FFD700" />
        <circle cx="52" cy="32" r="4.5" fill="#FFD700" />
      </>
    ),
  },
  "Taco de Chicken": {
    label: "Taco de Chicken",
    content: (
      <>
        {/* Shell */}
        <path d="M 8 54 Q 40 12 72 54"
          stroke="#C8A45A" strokeWidth="11" fill="none" strokeLinecap="round" />
        {/* Lettuce */}
        <ellipse cx="40" cy="57" rx="26" ry="8" fill="#228B22" />
        {/* Chicken (white) */}
        <ellipse cx="40" cy="54" rx="16" ry="6" fill="#FFFACD" />
        {/* Lettuce frills */}
        <path d="M 17 56 Q 21 51 25 56" stroke="#32CD32" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M 55 56 Q 59 51 63 56" stroke="#32CD32" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      </>
    ),
  },
  "Taco de CHICKEN": {
    label: "Taco de CHICKEN",
    content: (
      <>
        {/* Glow */}
        <ellipse cx="40" cy="42" rx="36" ry="30" fill="#FFD700" opacity="0.18" />
        {/* Shell – golden */}
        <path d="M 8 54 Q 40 12 72 54"
          stroke="#DAA520" strokeWidth="11" fill="none" strokeLinecap="round" />
        {/* Filling */}
        <ellipse cx="40" cy="57" rx="26" ry="8" fill="#228B22" />
        {/* Chicken */}
        <ellipse cx="40" cy="53" rx="18" ry="7" fill="#FFFACD" />
        {/* Stars */}
        <text x="12" y="32" fontSize="13" fill="#FFD700">★</text>
        <text x="57" y="28" fontSize="11" fill="#FFD700">★</text>
        <text x="34" y="22" fontSize="9" fill="#FFD700">★</text>
      </>
    ),
  },
};

const FALLBACK = TACO_CONTENTS["Cooking..."];

export default function TacoIcon({ bandLabel, size = 80, className }: { bandLabel: string; size?: number; className?: string }) {
  const taco = TACO_CONTENTS[bandLabel] ?? FALLBACK;
  const height = Math.round(size * 72 / 80);
  return (
    <div className={className}>
      <svg viewBox="0 0 80 72" width={size} height={height} aria-label={taco.label}>
        {taco.content}
      </svg>
    </div>
  );
}
