import TacoIcon from "@/components/TacoIcon";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const BANDS = [
  {
    label: "Taco de Habanero",
    range: "0 – 20",
    sentiment: "Extreme Bearish",
    description: "Market deeply fearful. Trump's posts signal strong negative pressure.",
    color: "#FF4444",
  },
  {
    label: "Taco de Chorizo",
    range: "21 – 40",
    sentiment: "Bearish",
    description: "Negative sentiment dominates. Caution advised across asset classes.",
    color: "#FF8C00",
  },
  {
    label: "Cooking...",
    range: "41 – 60",
    sentiment: "Neutral",
    description: "Mixed signals. Markets are digesting Trump's latest activity.",
    color: "#FFD700",
  },
  {
    label: "Taco de Frijoles",
    range: "61 – 80",
    sentiment: "Bullish",
    description: "Positive sentiment building. Risk assets showing upward momentum.",
    color: "#32CD32",
  },
  {
    label: "Taco de CHICKEN",
    range: "81 – 100",
    sentiment: "Extreme Bullish",
    description: "Maximum optimism. Trump's posts driving strong market confidence.",
    color: "#008000",
  },
];

export default function BandLegend() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Index Guide</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          {BANDS.map((band) => (
            <div
              key={band.label}
              className="flex flex-col items-center text-center gap-2 rounded-xl p-4"
              style={{ backgroundColor: band.color + "11", border: `1px solid ${band.color}33` }}
            >
              <TacoIcon bandLabel={band.label} size={48} />
              <p className="text-xs font-bold" style={{ color: band.color }}>
                {band.sentiment}
              </p>
              <p className="text-sm font-semibold text-foreground/90">{band.label}</p>
              <p className="text-xs text-muted-foreground font-mono">{band.range}</p>
              <p className="text-xs text-muted-foreground/80 leading-relaxed">{band.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
