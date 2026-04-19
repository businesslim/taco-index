export type SortKey = "active_desc" | "active_asc" | "score_desc" | "score_asc" | "updated_desc" | "updated_asc";

const OPTIONS: { key: SortKey; label: string }[] = [
  { key: "active_desc",  label: "Most Active" },
  { key: "active_asc",   label: "Least Active" },
  { key: "score_desc",   label: "Highest Score" },
  { key: "score_asc",    label: "Lowest Score" },
  { key: "updated_desc", label: "Latest Post" },
  { key: "updated_asc",  label: "Oldest Post" },
];

export function SortControl({
  value,
  onChange,
}: {
  value: SortKey;
  onChange: (key: SortKey) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as SortKey)}
      className="text-xs rounded-full px-3 py-1 bg-muted text-muted-foreground border-0 cursor-pointer hover:text-foreground focus:outline-none focus:ring-1 focus:ring-amber-500"
    >
      {OPTIONS.map((opt) => (
        <option key={opt.key} value={opt.key}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
