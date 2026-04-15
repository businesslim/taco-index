import {
  fetchCurrentIndex,
  fetchRecentTweets,
} from "@/lib/api";
import GaugeMeter from "@/components/GaugeMeter";
import TweetFeed from "@/components/TweetFeed";
import MarketTicker from "@/components/MarketTicker";
import IndexHistoryChart from "@/components/IndexHistoryChart";
import BandLegend from "@/components/BandLegend";

export const revalidate = 60;

export default async function HomePage() {
  const [currentIndex, recentTweets] = await Promise.all([
    fetchCurrentIndex().catch(() => ({
      index_value: 50,
      band_label: "Cooking...",
      band_color: "#FFD700",
      tweet_count: 0,
      calculated_at: null,
      last_post_at: null,
    })),
    fetchRecentTweets(10).catch(() => []),
  ]);

  return (
    <div className="flex flex-col gap-8">
      {/* 설명 문구 */}
      <p className="text-gray-400 text-sm leading-relaxed">
        The TACO Index analyzes Donald Trump&apos;s Truth Social activity to gauge financial market sentiment. Each post is scored for market relevance and direction, giving you a real-time pulse on how Trump&apos;s words move crypto, equities, and commodities.
      </p>

      {/* TACO Index 게이지 */}
      <section className="bg-gray-900 rounded-2xl p-8 flex flex-col items-center gap-2">
        <GaugeMeter
          value={currentIndex.index_value}
          label={currentIndex.band_label}
          color={currentIndex.band_color}
        />
        {currentIndex.calculated_at ? (
          <p className="text-gray-500 text-sm">
            Last updated:{" "}
            {new Date(currentIndex.calculated_at).toLocaleString()}
          </p>
        ) : (
          <p className="text-gray-600 text-sm">No data yet</p>
        )}
        {(() => {
          if (!currentIndex.last_post_at) return null;
          const hoursAgo = (Date.now() - new Date(currentIndex.last_post_at).getTime()) / 36e5;
          if (hoursAgo < 48) return null;
          return (
            <p className="text-yellow-600 text-xs text-center max-w-sm mt-1">
              ⚠️ No Truth Social activity detected in the past 48 hours. The index may not reflect current market conditions.
            </p>
          );
        })()}
      </section>

      {/* 시장 데이터 */}
      <MarketTicker />

      {/* Index 이력 차트 */}
      <section className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-4">Index History</h2>
        <IndexHistoryChart />
      </section>

      {/* 밴드 범례 */}
      <BandLegend />

      {/* 트윗 피드 */}
      <section className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Posts</h2>
        <TweetFeed tweets={recentTweets} />
      </section>
    </div>
  );
}
