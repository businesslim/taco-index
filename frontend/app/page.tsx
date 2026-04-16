import {
  fetchCurrentIndex,
  fetchRecentTweets,
} from "@/lib/api";
import GaugeMeter from "@/components/GaugeMeter";
import TweetFeed from "@/components/TweetFeed";
import TopPostFeed from "@/components/TopPostFeed";
import MarketTicker from "@/components/MarketTicker";
import dynamic from "next/dynamic";
const IndexHistoryChart = dynamic(() => import("@/components/IndexHistoryChart"), { ssr: false });
import BandLegend from "@/components/BandLegend";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
    fetchRecentTweets(20).catch(() => []),
  ]);

  return (
    <div className="flex flex-col gap-8">
      {/* Hero 설명 */}
      <div className="flex flex-col gap-1.5">
        <h2 className="text-lg font-semibold text-foreground">What is TACO Index?</h2>
        <p className="text-muted-foreground text-sm leading-relaxed max-w-2xl">
          The TACO Index analyzes Donald Trump&apos;s Truth Social activity to gauge financial market sentiment. Each post is scored for market relevance and direction, giving you a real-time pulse on how Trump&apos;s words move crypto, equities, and commodities.
        </p>
      </div>

      {/* 상단 2컬럼: 게이지(좌) + 최근 포스트(우) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 좌: TACO Index 게이지 */}
        <Card>
          <CardContent className="flex flex-col items-center gap-2 pt-6 pb-6">
            <GaugeMeter
              value={currentIndex.index_value}
              label={currentIndex.band_label}
              color={currentIndex.band_color}
              compact
            />
            {currentIndex.calculated_at ? (
              <p className="text-muted-foreground text-xs">
                Last updated:{" "}
                {new Date(currentIndex.calculated_at).toLocaleString()}
              </p>
            ) : (
              <p className="text-muted-foreground/60 text-xs">No data yet</p>
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
          </CardContent>
        </Card>

        {/* 우: 최근 마켓 포스트 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Latest Market Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <TopPostFeed tweets={recentTweets} />
          </CardContent>
        </Card>
      </div>

      {/* 시장 데이터 */}
      <MarketTicker />

      {/* Index 이력 차트 */}
      <Card>
        <CardHeader>
          <CardTitle>Index History</CardTitle>
        </CardHeader>
        <CardContent>
          <IndexHistoryChart />
        </CardContent>
      </Card>

      {/* 밴드 범례 */}
      <BandLegend />

      {/* 트윗 피드 */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Posts</CardTitle>
        </CardHeader>
        <CardContent>
          <TweetFeed tweets={recentTweets} />
        </CardContent>
      </Card>
    </div>
  );
}
