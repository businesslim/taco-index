export type SortKey = "score_desc" | "score_asc" | "updated_desc" | "updated_asc";

const OPTIONS: { key: SortKey; label: string }[] = [
  { key: "score_desc", label: "Score ↓" },
  { key: "score_asc",  label: "Score ↑" },
  { key: "updated_desc", label: "Latest post" },
  { key: "updated_asc",  label: "Oldest post" },
];

export function SortControl({
  value,
  onChange,
}: {
  value: SortKey;
  onChange: (key: SortKey) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground/60 text-xs">Sort</span>
      <div className="flex gap-1.5 flex-wrap">
        {OPTIONS.map((opt) => (
          <button
            key={opt.key}
            onClick={() => onChange(opt.key)}
            className={`px-3 py-1 rounded-full text-xs transition-colors ${
              value === opt.key
                ? "bg-amber-500/20 border border-amber-500 text-amber-400"
                : "bg-muted text-muted-foreground hover:text-foreground"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
