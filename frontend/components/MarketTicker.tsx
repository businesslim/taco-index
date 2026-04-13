import { fetchMarketPrices, MarketAsset } from "@/lib/api";

async function fetchCrypto(): Promise<MarketAsset[]> {
  try {
    const res = await fetch(
      "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana&order=market_cap_desc",
      { next: { revalidate: 300 } }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.map((coin: { symbol: string; current_price: number; price_change_percentage_24h: number }) => ({
      symbol: coin.symbol.toUpperCase(),
      label: coin.symbol.toUpperCase(),
      price: coin.current_price,
      change_percent: coin.price_change_percentage_24h,
    }));
  } catch {
    return [];
  }
}

function formatCrypto(price: number): string {
  return "$" + price.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function formatIndex(price: number): string {
  return price.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function formatGold(price: number): string {
  return "$" + price.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function CategoryBox({
  title,
  assets,
  formatPrice,
}: {
  title: string;
  assets: MarketAsset[];
  formatPrice: (p: number) => string;
}) {
  return (
    <div className="bg-gray-900 rounded-2xl p-5 flex flex-col gap-4">
      <h3 className="text-xs text-gray-500 uppercase tracking-wide font-medium">{title}</h3>
      {assets.length === 0 ? (
        <p className="text-gray-600 text-sm">Data unavailable</p>
      ) : (
        <div className="flex flex-col gap-3">
          {assets.map((asset) => {
            const isUp = asset.change_percent >= 0;
            return (
              <div key={asset.symbol} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-300">{asset.label}</span>
                <div className="flex flex-col items-end gap-0.5">
                  <span className="text-sm font-bold">{formatPrice(asset.price)}</span>
                  <span className={`text-xs font-medium ${isUp ? "text-green-400" : "text-red-400"}`}>
                    {isUp ? "▲" : "▼"} {Math.abs(asset.change_percent).toFixed(2)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default async function MarketTicker() {
  const fetchedAt = new Date();

  const [crypto, market] = await Promise.all([
    fetchCrypto(),
    fetchMarketPrices(),
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

  return (
    <div className="flex flex-col gap-2">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <CategoryBox title="Crypto" assets={crypto} formatPrice={formatCrypto} />
        <CategoryBox title="US Equities" assets={market.equities} formatPrice={formatIndex} />
        <CategoryBox title="Commodities" assets={market.commodities} formatPrice={formatGold} />
      </div>
      <p className="text-xs text-gray-600 text-right">Last updated: {updatedAt}</p>
    </div>
  );
}
