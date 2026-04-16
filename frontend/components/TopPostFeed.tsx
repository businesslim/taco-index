import { TweetWithScore } from "@/lib/api";

interface Props {
  tweets: TweetWithScore[];
}

export default function TopPostFeed({ tweets }: Props) {
  const posts = tweets.filter((t) => t.market_relevant).slice(0, 5);

  if (posts.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">No recent market posts.</p>
    );
  }

  return (
    <ul className="flex flex-col divide-y divide-border">
      {posts.map((tweet) => (
        <li key={tweet.tweet_id}>
          <a
            href={`https://truthsocial.com/@realDonaldTrump/posts/${tweet.tweet_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 py-3 hover:opacity-80 transition-opacity"
          >
            {/* Badge */}
            <span
              className="shrink-0 text-xs font-bold font-mono px-2 py-0.5 rounded"
              style={{
                backgroundColor: tweet.band_color + "22",
                color: tweet.band_color,
                border: `1px solid ${tweet.band_color}44`,
              }}
            >
              {tweet.final_score}
            </span>
            {/* Content */}
            <p className="text-sm text-foreground/80 truncate">
              {tweet.content}
            </p>
          </a>
        </li>
      ))}
    </ul>
  );
}
