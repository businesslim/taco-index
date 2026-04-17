import json
import anthropic
from app.config import settings

_client: anthropic.Anthropic | None = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client

DOMAIN_PROMPTS = {
    "crypto": """You are a crypto market analyst. Analyze the following post and rate its sentiment toward cryptocurrency markets on a scale of 0-100.
0-20: Extreme Bearish (bans, sanctions, strict regulation)
21-40: Bearish (negative regulatory signals, market uncertainty)
41-60: Neutral (unrelated or ambiguous)
61-80: Bullish (pro-market, pro-crypto statements)
81-100: Extreme Bullish (direct endorsement, major deregulation)
Respond ONLY with JSON: {"score": <int>, "reasoning": "<one sentence>"}""",

    "stock": """You are an equity market analyst. Analyze the following post and rate its sentiment toward stock markets on a scale of 0-100.
0-20: Extreme Bearish (crash warnings, severe recession, systemic risk)
21-40: Bearish (economic slowdown, earnings concerns, rate fears)
41-60: Neutral (unrelated or ambiguous)
61-80: Bullish (growth optimism, strong earnings, rate cuts expected)
81-100: Extreme Bullish (boom forecasts, major stimulus, record highs)
Respond ONLY with JSON: {"score": <int>, "reasoning": "<one sentence>"}""",

    "macro": """You are a macroeconomic analyst. Analyze the following post and rate its sentiment toward the global economy on a scale of 0-100.
0-20: Extreme Bearish (depression risk, hyperinflation, systemic collapse)
21-40: Bearish (recession signals, tightening, stagflation)
41-60: Neutral (unrelated or ambiguous)
61-80: Bullish (soft landing, moderate growth, easing signals)
81-100: Extreme Bullish (boom, major fiscal stimulus, strong GDP)
Respond ONLY with JSON: {"score": <int>, "reasoning": "<one sentence>"}""",

    "gold": """You are a precious metals analyst. Analyze the following post and rate its sentiment toward gold and safe-haven assets on a scale of 0-100.
0-20: Extreme Bearish (no inflation risk, strong dollar, risk-on)
21-40: Bearish (mild risk-on, low inflation expectations)
41-60: Neutral (unrelated or ambiguous)
61-80: Bullish (inflation concerns, dollar weakness, uncertainty)
81-100: Extreme Bullish (crisis, hyperinflation, major geopolitical risk)
Respond ONLY with JSON: {"score": <int>, "reasoning": "<one sentence>"}""",
}

BULLISH_KEYWORDS = {
    "bitcoin", "btc", "crypto", "blockchain", "deal", "win", "boom",
    "bull", "moon", "approve", "support", "freedom", "rich", "wealth",
    "opportunity", "growth", "rise", "buy", "invest", "innovation",
}

BEARISH_KEYWORDS = {
    "tariff", "ban", "sanction", "war", "crash", "fraud", "illegal",
    "crackdown", "restrict", "block", "fine", "penalty", "tax", "regulation",
    "seizure", "probe", "recession", "inflation", "collapse",
}


def _keyword_score(text: str) -> int:
    words = set(text.lower().split())
    bull = len(words & BULLISH_KEYWORDS)
    bear = len(words & BEARISH_KEYWORDS)
    if bull + bear == 0:
        return 50
    return round((bull / (bull + bear)) * 100)


def score_influencer_post(content: str, domain: str) -> dict:
    """
    Returns:
        {"llm_score": int, "keyword_score": int, "final_score": int, "reasoning": str}
    """
    prompt = DOMAIN_PROMPTS.get(domain, DOMAIN_PROMPTS["macro"])
    client = _get_client()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system=prompt,
        messages=[{"role": "user", "content": f'Analyze this post:\n\n"{content}"'}],
    )

    try:
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        llm_score = max(0, min(100, int(data["score"])))
        reasoning = str(data.get("reasoning", ""))
    except (json.JSONDecodeError, KeyError, ValueError, IndexError):
        llm_score, reasoning = 50, "Analysis unavailable"

    keyword_score = _keyword_score(content)
    final_score = round(llm_score * 0.85 + keyword_score * 0.15)

    return {
        "llm_score": llm_score,
        "keyword_score": keyword_score,
        "final_score": final_score,
        "reasoning": reasoning,
    }
