BULLISH_KEYWORDS = [
    "bitcoin", "btc", "crypto", "cryptocurrency", "blockchain",
    "deal", "great", "win", "winning", "boom", "bull", "moon",
    "approve", "approved", "support", "freedom", "rich", "wealth",
    "opportunity", "growth", "rise", "buy", "invest", "innovation",
    "deregulate", "deregulation", "pro-crypto", "digital asset",
]

BEARISH_KEYWORDS = [
    "tariff", "tariffs", "ban", "banned", "sanction", "sanctions",
    "war", "crash", "fake", "fraud", "illegal", "crackdown",
    "investigation", "restrict", "restriction", "block", "blocked",
    "fine", "penalty", "tax", "taxes", "regulation", "regulate",
    "seizure", "confiscate", "probe", "subpoena",
]

def compute_keyword_score(text: str) -> int:
    """텍스트에서 키워드를 스캔해 0~100 점수를 반환한다. 50이 중립."""
    if not text:
        return 50

    lower = text.lower()
    bullish_count = sum(1 for kw in BULLISH_KEYWORDS if kw in lower)
    bearish_count = sum(1 for kw in BEARISH_KEYWORDS if kw in lower)

    total = bullish_count + bearish_count
    if total == 0:
        return 50

    raw = bullish_count / total  # 0.0 ~ 1.0
    score = int(raw * 100)
    return max(0, min(100, score))
