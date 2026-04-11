import { TweetWithScore } from "@/lib/api";

interface Props {
  tweets: TweetWithScore[];
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function TweetFeed({ tweets }: Props) {
  if (tweets.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No posts yet. Data will appear after the first pipeline run.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-4">
      {tweets.map((tweet) => (
        <li
          key={tweet.tweet_id}
          className="border border-gray-800 rounded-xl p-4 hover:border-gray-600 transition-colors"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400 uppercase tracking-wide font-medium">
              {tweet.source === "truth_social" ? "Truth Social" : "X (Twitter)"}
            </span>
            <span className="text-xs text-gray-500">{timeAgo(tweet.posted_at)}</span>
          </div>
          <p className="text-sm text-gray-200 mb-3 leading-relaxed">{tweet.content}</p>
          <div className="flex items-center gap-3 flex-wrap">
            <span
              className="text-sm font-bold px-3 py-1 rounded-full"
              style={{
                backgroundColor: tweet.band_color + "22",
                color: tweet.band_color,
                border: `1px solid ${tweet.band_color}44`,
              }}
            >
              {tweet.final_score} · {tweet.band_label}
            </span>
            {tweet.llm_reasoning && (
              <span className="text-xs text-gray-500 italic">
                &ldquo;{tweet.llm_reasoning}&rdquo;
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
