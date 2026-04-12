interface CoinData {
  id: string;
  symbol: string;
  current_price: number;
  price_change_percentage_24h: number;
}

async function fetchCoinPrices(): Promise<{ coins: CoinData[]; fetchedAt: Date }> {
  try {
    const res = await fetch(
      "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana&order=market_cap_desc",
      { next: { revalidate: 300 } }
    );
    if (!res.ok) return { coins: [], fetchedAt: new Date() };
    return { coins: await res.json(), fetchedAt: new Date() };
  } catch {
    return { coins: [], fetchedAt: new Date() };
  }
}

export default async function CoinPriceTicker() {
  const { coins, fetchedAt } = await fetchCoinPrices();

  if (coins.length === 0) {
    return null;
  }

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
    <div className="bg-gray-900 rounded-2xl p-6">
      <div className="flex gap-8 flex-wrap">
        {coins.map((coin) => {
          const isUp = coin.price_change_percentage_24h >= 0;
          return (
            <div key={coin.id} className="flex flex-col gap-1">
              <span className="text-gray-400 text-xs uppercase tracking-wide font-medium">
                {coin.symbol}
              </span>
              <span className="text-lg font-bold">
                ${coin.current_price.toLocaleString()}
              </span>
              <span
                className={`text-sm font-medium ${
                  isUp ? "text-green-400" : "text-red-400"
                }`}
              >
                {isUp ? "▲" : "▼"}{" "}
                {Math.abs(coin.price_change_percentage_24h).toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>
      <p className="text-xs text-gray-500 mt-4">Last updated: {updatedAt}</p>
    </div>
  );
}
