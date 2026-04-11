import pytest
from app.scraper.truth_social import parse_feed_entries

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <guid>https://truthsocial.com/@realDonaldTrump/posts/112345</guid>
      <title>Bitcoin is the future!</title>
      <description>Bitcoin is the future of America. We will make crypto great again!</description>
      <pubDate>Fri, 11 Apr 2026 10:00:00 +0000</pubDate>
    </item>
    <item>
      <guid>https://truthsocial.com/@realDonaldTrump/posts/112346</guid>
      <title>New tariffs</title>
      <description>New tariffs on China starting immediately.</description>
      <pubDate>Fri, 11 Apr 2026 09:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""

def test_parse_feed_entries_extracts_fields():
    import feedparser
    feed = feedparser.parse(SAMPLE_RSS)
    entries = parse_feed_entries(feed.entries)
    assert len(entries) == 2

def test_parse_feed_entry_has_required_fields():
    import feedparser
    feed = feedparser.parse(SAMPLE_RSS)
    entries = parse_feed_entries(feed.entries)
    entry = entries[0]
    assert entry["source"] == "truth_social"
    assert "Bitcoin" in entry["content"]
    assert entry["tweet_id"] == "https://truthsocial.com/@realDonaldTrump/posts/112345"
    assert entry["posted_at"] is not None

def test_parse_feed_entries_empty():
    entries = parse_feed_entries([])
    assert entries == []

def test_parse_feed_entries_skips_malformed():
    # Entry with no guid should be skipped or handled gracefully
    import feedparser
    bad_rss = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item><title>No guid here</title></item>
    </channel></rss>"""
    feed = feedparser.parse(bad_rss)
    entries = parse_feed_entries(feed.entries)
    # Should not raise, result can be 0 or 1 entries
    assert isinstance(entries, list)
