import { TweetWithScore } from "@/lib/api";
import TweetItem from "./TweetItem";

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
        <li key={tweet.tweet_id}>
          <TweetItem tweet={tweet} timeAgo={timeAgo(tweet.posted_at)} />
        </li>
      ))}
    </ul>
  );
}
