import json
import anthropic
from app.config import settings

_client: anthropic.Anthropic | None = None

def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client

SYSTEM_PROMPT = """You are a financial sentiment analyst specializing in crypto markets.
Analyze Trump's social media post and score its potential impact on cryptocurrency markets.

Score from 0 to 100:
- 0-20: Extremely bearish (bans, sanctions, heavy regulation on crypto)
- 21-40: Bearish (negative regulatory signals, market uncertainty)
- 41-60: Neutral (unrelated to crypto/markets, or ambiguous signals)
- 61-80: Bullish (positive economic signals, pro-crypto or pro-market statements)
- 81-100: Extremely bullish (direct crypto endorsement, major deregulation)

Respond in JSON only, no other text: {"score": <integer 0-100>, "reasoning": "<one sentence explanation>"}"""

def analyze_tweet(content: str, keyword_hints: list[str]) -> tuple[int, str]:
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
        data = json.loads(message.content[0].text)
        score = max(0, min(100, int(data["score"])))
        reasoning = str(data.get("reasoning", ""))
        return score, reasoning
    except (json.JSONDecodeError, KeyError, ValueError, IndexError):
        return 50, "Analysis unavailable"
