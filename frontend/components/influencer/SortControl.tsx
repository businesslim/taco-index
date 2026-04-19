export type SortKey = "score_desc" | "score_asc" | "updated_desc" | "updated_asc" | "active_desc" | "active_asc";

const BUTTONS: { asc: SortKey; desc: SortKey; label: string }[] = [
  { label: "Active", desc: "active_desc", asc: "active_asc" },
  { label: "Score", desc: "score_desc", asc: "score_asc" },
  { label: "Post",  desc: "updated_desc", asc: "updated_asc" },
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
      <div className="flex gap-1.5">
        {BUTTONS.map((btn) => {
          const isDesc = value === btn.desc;
          const isAsc = value === btn.asc;
          const isActive = isDesc || isAsc;

          const handleClick = () => {
            if (!isActive) onChange(btn.desc);
            else if (isDesc) onChange(btn.asc);
            else onChange(btn.desc);
          };

          return (
            <button
              key={btn.label}
              onClick={handleClick}
              className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs transition-colors ${
                isActive
                  ? "bg-amber-500/20 border border-amber-500 text-amber-400"
                  : "bg-muted text-muted-foreground hover:text-foreground"
              }`}
            >
              {btn.label}
              <span className="opacity-70">
                {isDesc ? "↓" : isAsc ? "↑" : "↕"}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
