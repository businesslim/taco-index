import anthropic
from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a financial sentiment analyst specializing in crypto markets.
Analyze Trump's social media post and score its potential impact on cryptocurrency markets.

Score from 0 to 100:
- 0-20: Extremely bearish (bans, sanctions, heavy regulation on crypto)
- 21-40: Bearish (negative regulatory signals, market uncertainty)
- 41-60: Neutral (unrelated to crypto/markets, or ambiguous signals)
- 61-80: Bullish (positive economic signals, pro-crypto or pro-market statements)
- 81-100: Extremely bullish (direct crypto endorsement, major deregulation)

Respond in JSON only, no other text: {"score": <integer 0-100>, "reasoning": "<one sentence explanation>"}"""

test_content = "GREAT!!!"

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": f'Analyze this Trump post:\n\n"{test_content}"'}],
)

raw = message.content[0].text
print("Raw response:", repr(raw))

import json
try:
    data = json.loads(raw)
    print("Parsed OK:", data)
except Exception as e:
    print("Parse failed:", e)
