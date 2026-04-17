import json
import anthropic
from app.config import settings

_client: anthropic.Anthropic | None = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client

_CRITICAL_RULE = """
Critical rules — judge by OVERALL DIRECTIONAL INTENT, not formal language:
- Confident bullish predictions ("about to rip higher", "going to moon", "massive rally coming") → score 75-90 even without stated reasoning.
- Confident bearish predictions ("crash incoming", "sell everything", "market is toast") → score 15-30.
- Financial slang: rip/surge/moon/pump/rally/squeeze = upward; dump/crater/crash/bleed/tank = downward.
- Informal tone or all-caps does NOT make a post neutral — judge the direction of the claim.
- Only score 41-60 if the post is genuinely unrelated to markets or truly ambiguous in direction."""

DOMAIN_PROMPTS = {
    "crypto": f"""You are a crypto market sentiment analyst. Rate the following post's sentiment toward cryptocurrency markets on a scale of 0-100.

0-20: Extreme Bearish — bans, seizures, major regulatory crackdown, exchange collapse
21-40: Bearish — negative regulatory signals, hack/fraud news, market fear
41-60: Neutral — unrelated to crypto, or genuinely ambiguous direction
61-80: Bullish — pro-crypto stance, adoption news, price optimism
81-100: Extreme Bullish — direct endorsement, ETF approval, landmark deregulation, massive adoption
{_CRITICAL_RULE}
Respond ONLY with JSON: {{"score": <int>, "reasoning": "<one sentence>"}}""",

    "stock": f"""You are an equity market sentiment analyst. Rate the following post's sentiment toward stock markets on a scale of 0-100.

0-20: Extreme Bearish — imminent crash warning, systemic collapse, severe recession
21-40: Bearish — slowdown concerns, earnings fears, rate hike risk, sell signals
41-60: Neutral — unrelated to equities, or genuinely ambiguous direction
61-80: Bullish — growth optimism, buy signals, earnings strength, rate cut hopes
81-100: Extreme Bullish — explosive rally prediction, major stimulus, historic boom forecast
{_CRITICAL_RULE}
Respond ONLY with JSON: {{"score": <int>, "reasoning": "<one sentence>"}}""",

    "macro": f"""You are a macroeconomic sentiment analyst. Rate the following post's sentiment toward the global economy on a scale of 0-100.

0-20: Extreme Bearish — depression risk, hyperinflation, systemic financial collapse
21-40: Bearish — recession signals, aggressive tightening, stagflation concerns
41-60: Neutral — unrelated to macro economy, or genuinely ambiguous direction
61-80: Bullish — soft landing, moderate growth, easing monetary policy
81-100: Extreme Bullish — economic boom, major stimulus, strong GDP growth
{_CRITICAL_RULE}
Respond ONLY with JSON: {{"score": <int>, "reasoning": "<one sentence>"}}""",

    "gold": f"""You are a precious metals sentiment analyst. Rate the following post's sentiment toward gold and safe-haven assets on a scale of 0-100.

0-20: Extreme Bearish — strong risk-on environment, strong dollar, no inflation risk
21-40: Bearish — mild risk-on, low inflation expectations, economic stability
41-60: Neutral — unrelated to gold/safe havens, or genuinely ambiguous direction
61-80: Bullish — inflation concerns, dollar weakness, geopolitical uncertainty
81-100: Extreme Bullish — crisis, hyperinflation, war, major geopolitical shock
{_CRITICAL_RULE}
Respond ONLY with JSON: {{"score": <int>, "reasoning": "<one sentence>"}}""",
}

DOMAIN_BULLISH_KEYWORDS: dict[str, set[str]] = {
    "crypto": {
        "bitcoin", "btc", "crypto", "blockchain", "moon", "bull", "pump",
        "adoption", "approve", "etf", "deregulation", "hodl", "accumulate",
        "buy", "rally", "surge", "higher", "rip", "explode", "breakout",
    },
    "stock": {
        "rally", "higher", "surge", "rip", "boom", "bull", "buy", "growth",
        "earnings", "record", "breakout", "explode", "squeeze", "upside",
        "opportunity", "invest", "wealth", "profit", "win", "soar",
    },
    "macro": {
        "growth", "recovery", "stimulus", "easing", "cut", "boom", "expansion",
        "strong", "gdp", "jobs", "employment", "optimism", "soft", "landing",
    },
    "gold": {
        "inflation", "crisis", "uncertainty", "hedge", "safe", "haven",
        "dollar", "weak", "geopolitical", "war", "risk", "fear", "protect",
    },
}

DOMAIN_BEARISH_KEYWORDS: dict[str, set[str]] = {
    "crypto": {
        "ban", "sanction", "crackdown", "hack", "fraud", "illegal", "seizure",
        "crash", "dump", "collapse", "regulation", "restrict", "fine", "probe",
    },
    "stock": {
        "crash", "recession", "slowdown", "correction", "sell", "dump",
        "crater", "tank", "bleed", "collapse", "fear", "tariff", "layoff",
        "earnings", "miss", "downgrade", "bear",
    },
    "macro": {
        "recession", "inflation", "stagflation", "tightening", "hike",
        "collapse", "crisis", "depression", "unemployment", "tariff", "war",
    },
    "gold": {
        "risk-on", "rally", "strong", "dollar", "stability", "growth",
        "recovery", "boom", "confidence",
    },
}


def _keyword_score(text: str, domain: str) -> int:
    words = set(text.lower().split())
    bull_kw = DOMAIN_BULLISH_KEYWORDS.get(domain, DOMAIN_BULLISH_KEYWORDS["macro"])
    bear_kw = DOMAIN_BEARISH_KEYWORDS.get(domain, DOMAIN_BEARISH_KEYWORDS["macro"])
    bull = len(words & bull_kw)
    bear = len(words & bear_kw)
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

    keyword_score = _keyword_score(content, domain)
    final_score = round(llm_score * 0.85 + keyword_score * 0.15)

    return {
        "llm_score": llm_score,
        "keyword_score": keyword_score,
        "final_score": final_score,
        "reasoning": reasoning,
    }
