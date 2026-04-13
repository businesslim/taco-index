interface AssetItem {
  symbol: string;
  label: string;
  price: number;
  changePercent: number;
  formatPrice: (p: number) => string;
}

interface Category {
  title: string;
  assets: AssetItem[];
}

async function fetchCrypto(): Promise<AssetItem[]> {
  try {
    const res = await fetch(
      "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana&order=market_cap_desc",
      { next: { revalidate: 300 } }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.map((coin: { id: string; symbol: string; current_price: number; price_change_percentage_24h: number }) => ({
      symbol: coin.symbol.toUpperCase(),
      label: coin.symbol.toUpperCase(),
      price: coin.current_price,
      changePercent: coin.price_change_percentage_24h,
      formatPrice: (p: number) => "$" + p.toLocaleString("en-US", { maximumFractionDigits: 2 }),
    }));
  } catch {
    return [];
  }
}

const YAHOO_SYMBOLS: Record<string, { label: string; formatPrice: (p: number) => string }> = {
  "^GSPC":  { label: "S&P 500",    formatPrice: (p) => p.toLocaleString("en-US", { maximumFractionDigits: 2 }) },
  "^NDX":   { label: "NASDAQ 100", formatPrice: (p) => p.toLocaleString("en-US", { maximumFractionDigits: 2 }) },
  "GC=F":   { label: "Gold",       formatPrice: (p) => "$" + p.toLocaleString("en-US", { maximumFractionDigits: 2 }) },
};

async function fetchYahoo(symbols: string[]): Promise<AssetItem[]> {
  try {
    const query = symbols.map(encodeURIComponent).join(",");
    const res = await fetch(
      `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${query}`,
      {
        next: { revalidate: 300 },
        headers: {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
          "Accept": "application/json",
        },
      }
    );
    if (!res.ok) return [];
    const data = await res.json();
    const quotes: Array<{ symbol: string; regularMarketPrice: number; regularMarketChangePercent: number }> =
      data.quoteResponse?.result ?? [];
    return quotes.map((q) => {
      const meta = YAHOO_SYMBOLS[q.symbol] ?? { label: q.symbol, formatPrice: (p: number) => p.toString() };
      return {
        symbol: q.symbol,
        label: meta.label,
        price: q.regularMarketPrice,
        changePercent: q.regularMarketChangePercent,
        formatPrice: meta.formatPrice,
      };
    });
  } catch {
    return [];
  }
}

function CategoryBox({ title, assets }: { title: string; assets: AssetItem[] }) {
  if (assets.length === 0) {
    return (
      <div className="bg-gray-900 rounded-2xl p-5 flex flex-col gap-3">
        <h3 className="text-xs text-gray-500 uppercase tracking-wide font-medium">{title}</h3>
        <p className="text-gray-600 text-sm">데이터를 불러올 수 없습니다</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-2xl p-5 flex flex-col gap-4">
      <h3 className="text-xs text-gray-500 uppercase tracking-wide font-medium">{title}</h3>
      <div className="flex flex-col gap-3">
        {assets.map((asset) => {
          const isUp = asset.changePercent >= 0;
          return (
            <div key={asset.symbol} className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-300">{asset.label}</span>
              <div className="flex flex-col items-end gap-0.5">
                <span className="text-sm font-bold">{asset.formatPrice(asset.price)}</span>
                <span className={`text-xs font-medium ${isUp ? "text-green-400" : "text-red-400"}`}>
                  {isUp ? "▲" : "▼"} {Math.abs(asset.changePercent).toFixed(2)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default async function MarketTicker() {
  const fetchedAt = new Date();

  const [crypto, equities, commodities] = await Promise.all([
    fetchCrypto(),
    fetchYahoo(["^GSPC", "^NDX"]),
    fetchYahoo(["GC=F"]),
  ]);

  const updatedAt = fetchedAt.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
    timeZoneName: "short",
  });

  const categories: Category[] = [
    { title: "가상자산", assets: crypto },
    { title: "미국 증시", assets: equities },
    { title: "원자재", assets: commodities },
  ];

  return (
    <div className="flex flex-col gap-2">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {categories.map((cat) => (
          <CategoryBox key={cat.title} title={cat.title} assets={cat.assets} />
        ))}
      </div>
      <p className="text-xs text-gray-600 text-right">Last updated: {updatedAt}</p>
    </div>
  );
}
