BULLISH_KEYWORDS = [
    # 크립토/디지털 자산
    "bitcoin", "btc", "crypto", "cryptocurrency", "blockchain", "digital asset",
    "deregulate", "deregulation", "pro-crypto",
    # 주식/경제 일반
    "deal", "trade deal", "agreement", "growth", "recovery", "surplus",
    "jobs", "employment", "rate cut", "stimulus", "boom", "rally",
    "earnings", "profit", "innovation", "opportunity",
    # 원자재/안전자산
    "gold", "silver", "oil", "energy",
    # 지정학 리스크 감소 (bullish: 분쟁 종식/완화)
    "ceasefire", "cease-fire", "peace deal", "peace agreement", "truce",
    "peace talk", "negotiation", "de-escalat", "end the war", "stop the war",
    "resolved", "resolution", "normalized", "normalization",
    # 시장 심리
    "great", "win", "winning", "strong", "approve", "approved",
    "support", "freedom", "wealth",
]

BEARISH_KEYWORDS = [
    # 규제/제재
    "tariff", "tariffs", "sanction", "sanctions", "ban", "banned",
    "crackdown", "investigate", "investigation", "restrict", "restriction",
    "regulate", "regulation", "fine", "penalty", "seizure", "confiscate",
    "probe", "subpoena", "illegal", "fraud",
    # 경제 위기
    "inflation", "deficit", "debt", "recession", "unemployment",
    "slowdown", "collapse", "crash", "crisis", "default", "bankrupt",
    # 지정학/갈등 (escalation)
    "war", "conflict", "invade", "invasion", "attack", "strike",
    "block", "blocked", "fake",
    # 세금
    "tax", "taxes",
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
