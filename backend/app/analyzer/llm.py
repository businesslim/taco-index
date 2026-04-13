import json
import anthropic
from app.config import settings

_client: anthropic.Anthropic | None = None

def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client

SYSTEM_PROMPT = """You are a financial sentiment analyst specializing in investment assets.
Analyze Trump's social media post and score its potential impact on investment asset markets.

First, determine if the post is market-relevant. Set market_relevant to false if the post is purely personal (e.g., congratulating someone, sports comments, birthday wishes, entertainment) with no policy, economic, or regulatory implications. Set market_relevant to true if the post touches on trade, policy, regulation, economy, geopolitics, or any factor that could influence investor sentiment.

Score from 0 to 100 (even for non-market-relevant posts, give your best estimate):
- 0-20: Extremely bearish (bans, sanctions, heavy regulation that would harm asset markets)
- 21-40: Bearish (negative regulatory signals, policy uncertainty hurting investor confidence)
- 41-60: Neutral (unrelated to markets, or ambiguous signals with no clear market impact)
- 61-80: Bullish (positive economic signals, pro-growth or pro-market policy statements)
- 81-100: Extremely bullish (major deregulation, strong pro-market stance, or direct asset endorsement)

Write the reasoning as a general market sentiment observation — avoid mentioning specific asset prices or crypto specifically. Focus on policy direction, economic conditions, and investor sentiment.

Respond in JSON only, no other text: {"score": <integer 0-100>, "reasoning": "<one sentence explanation>", "market_relevant": <true or false>}"""""

def analyze_tweet(content: str, keyword_hints: list[str]) -> tuple[int, str, bool]:
    """트윗을 분석해 (점수 0~100, 근거 텍스트) 를 반환한다.

    Args:
        content: 트윗 텍스트
        keyword_hints: 사전 감지된 키워드 목록 (LLM 컨텍스트 힌트용)

    Returns:
        (score, reasoning) tuple
    """
    hint_text = ""
    if keyword_hints:
        hint_text = f"\n\nPre-detected keywords: {', '.join(keyword_hints)}"

    client = get_client()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f'Analyze this Trump post:{hint_text}\n\n"{content}"'
            }
        ],
    )

    try:
        raw = message.content[0].text.strip()
        # 마크다운 코드블록 제거 (```json ... ``` 또는 ``` ... ```)
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        score = max(0, min(100, int(data["score"])))
        reasoning = str(data.get("reasoning", ""))
        market_relevant = bool(data.get("market_relevant", True))
        return score, reasoning, market_relevant
    except (json.JSONDecodeError, KeyError, ValueError, IndexError):
        return 50, "Analysis unavailable", True
