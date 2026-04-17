"""
TACO Index Telegram Bot

- /start  : 알림 구독
- /stop   : 구독 해제
- /index  : 현재 TACO Index 조회
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.config import settings
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

SUBSCRIBERS_KEY = "telegram:subscribers"

TACO_EMOJI = {
    "Taco de Habanero": "🌶️",
    "Taco de Chorizo":  "🥩",
    "Cooking...":       "⏳",
    "Taco de Frijoles": "🌮",
    "Taco de CHICKEN":  "🏆",
}


def _band_emoji(band_label: str) -> str:
    return TACO_EMOJI.get(band_label, "🌮")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    redis = await get_redis()
    await redis.sadd(SUBSCRIBERS_KEY, chat_id)
    await update.message.reply_text(
        "🌮 *Welcome to TACO Index!*\n\n"
        "The TACO Index analyzes Donald Trump's Truth Social activity to gauge financial market sentiment. "
        "Each post is scored for market relevance and direction, giving you a real-time pulse on how Trump's words move crypto, equities, and commodities.\n\n"
        "• `/index` — Get current index\n"
        "• `/stop` — Unsubscribe",
        parse_mode="Markdown",
    )


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    redis = await get_redis()
    await redis.srem(SUBSCRIBERS_KEY, chat_id)
    await update.message.reply_text("구독이 해제됐어요. 다시 받으려면 /start 를 입력하세요.")


async def cmd_index(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    redis = await get_redis()
    cached = await redis.get("taco:current_index")
    if not cached or ":" not in cached:
        await update.message.reply_text("아직 데이터가 없어요. 잠시 후 다시 시도해주세요.")
        return

    index_value_str, band_label = cached.split(":", 1)
    index_value = int(index_value_str)
    emoji = _band_emoji(band_label)

    await update.message.reply_text(
        f"🌮 *TACO Index: {index_value}*\n"
        f"*{band_label}*\n\n"
        f"🔗 taco-index.com",
        parse_mode="Markdown",
    )


async def notify_subscribers(band_label: str, index_value: int, new_posts: int, latest_post: dict | None = None) -> None:
    """파이프라인 완료 후 구독자에게 알림 발송."""
    if not settings.telegram_bot_token:
        return

    redis = await get_redis()
    subscriber_ids = await redis.smembers(SUBSCRIBERS_KEY)
    if not subscriber_ids:
        return

    emoji = _band_emoji(band_label)

    post_section = ""
    if latest_post and latest_post.get("content"):
        content = latest_post["content"]
        preview = content[:280] + "…" if len(content) > 280 else content
        post_section = f"\n\n📝 *Latest Post*\n_{preview}_"

    text = (
        f"🌮 *TACO Index Update*\n\n"
        f"{emoji} Score: *{index_value}* · {band_label}"
        f"{post_section}\n\n"
        f"👉 taco\\-index\\.com"
    )

    from telegram import Bot
    bot = Bot(token=settings.telegram_bot_token)
    async with bot:
        for chat_id in subscriber_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"Failed to send to {chat_id}: {e}")


def build_application():
    """봇 Application 객체 생성."""
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("index", cmd_index))
    return app


async def run_bot_polling():
    """polling 방식으로 봇 실행 (Railway 환경)."""
    if not settings.telegram_bot_token:
        logger.info("TELEGRAM_BOT_TOKEN not set, skipping bot startup")
        return

    logger.info("Starting Telegram bot (polling)...")
    application = build_application()
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot polling started")
