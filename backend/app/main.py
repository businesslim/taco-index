from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.redis_client import close_redis

app = FastAPI(title="TACO Index API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown():
    await close_redis()

@app.get("/health")
async def health():
    return {"status": "ok"}
