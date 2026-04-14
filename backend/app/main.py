import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.redis_client import close_redis
from app.scheduler.jobs import start_scheduler, run_pipeline
from app.api.index import router as index_router
from app.api.tweets import router as tweets_router
from app.api.bands import router as bands_router
from app.api.market import router as market_router
from app.telegram_bot import run_bot_polling

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    asyncio.create_task(run_pipeline())  # 서버 시작 시 즉시 1회 실행
    asyncio.create_task(run_bot_polling())
    yield
    await close_redis()

app = FastAPI(title="TACO Index API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(index_router)
app.include_router(tweets_router)
app.include_router(bands_router)
app.include_router(market_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
