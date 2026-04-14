"use client";

import { useState } from "react";
import { TweetWithScore } from "@/lib/api";
import TacoIcon from "@/components/TacoIcon";

const COLLAPSE_THRESHOLD = 280;

interface Props {
  tweet: TweetWithScore;
  timeAgo: string;
}

export default function TweetItem({ tweet, timeAgo }: Props) {
  const isLong = tweet.content.length > COLLAPSE_THRESHOLD;
  const [expanded, setExpanded] = useState(false);

  const displayContent =
    isLong && !expanded
      ? tweet.content.slice(0, COLLAPSE_THRESHOLD) + "…"
      : tweet.content;

  return (
    <a
      href={`https://truthsocial.com/@realDonaldTrump/posts/${tweet.tweet_id}`}
      target="_blank"
      rel="noopener noreferrer"
      className="block border border-gray-800 rounded-xl p-4 hover:border-gray-600 transition-colors cursor-pointer"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide font-medium">
          {tweet.source === "truth_social" ? "Truth Social" : "X (Twitter)"}
        </span>
        <span className="text-xs text-gray-500">{timeAgo}</span>
      </div>
      <p className="text-sm text-gray-200 mb-2 leading-relaxed break-words">
        {displayContent}
      </p>
      {isLong && (
        <button
          onClick={(e) => {
            e.preventDefault();
            setExpanded((prev) => !prev);
          }}
          className="text-xs text-gray-400 hover:text-gray-200 mb-3 transition-colors"
        >
          {expanded ? "Show less ▲" : "Show more ▼"}
        </button>
      )}
      <div className="flex items-center gap-3 flex-wrap">
        {tweet.market_relevant ? (
          <span
            className="inline-flex items-center gap-1.5 text-sm font-bold px-3 py-1 rounded-full"
            style={{
              backgroundColor: tweet.band_color + "22",
              color: tweet.band_color,
              border: `1px solid ${tweet.band_color}44`,
            }}
          >
            <TacoIcon bandLabel={tweet.band_label} size={24} className="shrink-0" />
            {tweet.final_score} · {tweet.band_label}
          </span>
        ) : (
          <span className="text-sm px-3 py-1 rounded-full bg-gray-800 text-gray-500 border border-gray-700">
            Off-topic
          </span>
        )}
        {tweet.llm_reasoning && (
          <span className="text-xs text-gray-500 italic">
            &ldquo;{tweet.llm_reasoning}&rdquo;
          </span>
        )}
      </div>
    </a>
  );
}
