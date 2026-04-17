from unittest.mock import patch, MagicMock
from app.influencer.scorer import score_influencer_post


def test_crypto_domain_returns_valid_score():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 75, "reasoning": "bullish crypto post"}')]
    with patch("app.influencer.scorer._get_client") as mock_get_client:
        mock_get_client.return_value.messages.create.return_value = mock_response
        result = score_influencer_post("Bitcoin is the future of money", "crypto")
    assert 0 <= result["final_score"] <= 100
    assert result["llm_score"] == 75
    assert "reasoning" in result


def test_final_score_uses_85_15_weights():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 80, "reasoning": "bullish"}')]
    with patch("app.influencer.scorer._get_client") as mock_get_client:
        mock_get_client.return_value.messages.create.return_value = mock_response
        result = score_influencer_post("Great market today buy stocks", "stock")
    expected = round(result["llm_score"] * 0.85 + result["keyword_score"] * 0.15)
    assert result["final_score"] == expected


def test_no_keywords_returns_50_keyword_score():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 50, "reasoning": "neutral"}')]
    with patch("app.influencer.scorer._get_client") as mock_get_client:
        mock_get_client.return_value.messages.create.return_value = mock_response
        result = score_influencer_post("Had a great lunch today with friends", "macro")
    assert result["keyword_score"] == 50


def test_stock_domain_uses_stock_prompt():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 60, "reasoning": "neutral stocks"}')]
    with patch("app.influencer.scorer._get_client") as mock_get_client:
        mock_get_client.return_value.messages.create.return_value = mock_response
        score_influencer_post("Markets are uncertain today", "stock")
    call_kwargs = mock_get_client.return_value.messages.create.call_args[1]
    system_prompt = call_kwargs.get("system", "")
    assert "equity" in system_prompt.lower() or "stock" in system_prompt.lower()


def test_score_clamped_to_0_100():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 150, "reasoning": "overflow"}')]
    with patch("app.influencer.scorer._get_client") as mock_get_client:
        mock_get_client.return_value.messages.create.return_value = mock_response
        result = score_influencer_post("some content", "gold")
    assert result["llm_score"] == 100
