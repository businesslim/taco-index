const CATEGORIES = [
  { key: null, label: "All" },
  { key: "Investor", label: "Investors" },
  { key: "CEO", label: "CEOs" },
  { key: "BigTech", label: "Big Tech" },
  { key: "Economist", label: "Economists" },
];

export function CategoryFilter({
  selected,
  onChange,
}: {
  selected: string | null;
  onChange: (cat: string | null) => void;
}) {
  return (
    <div className="flex gap-2 flex-wrap">
      {CATEGORIES.map((cat) => (
        <button
          key={cat.key ?? "all"}
          onClick={() => onChange(cat.key)}
          className={`px-3 py-1 rounded-full text-xs transition-colors ${
            selected === cat.key
              ? "bg-amber-500/20 border border-amber-500 text-amber-400"
              : "bg-muted text-muted-foreground hover:text-foreground"
          }`}
        >
          {cat.label}
        </button>
      ))}
    </div>
  );
}
