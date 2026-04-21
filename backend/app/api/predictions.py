from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import AsyncSessionLocal
from app.models.prediction import User, Prediction, AssetEnum, TimeframeEnum, DirectionEnum, ResultEnum
from app.models.asset_price import AssetPriceHistory

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


async def get_or_create_user(email: str, name: Optional[str], image: Optional[str], db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=email,
            name=name,
            image=image,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def evaluates_at_from_timeframe(timeframe: TimeframeEnum) -> datetime:
    now = datetime.now(timezone.utc)
    if timeframe == TimeframeEnum.daily:
        return now + timedelta(days=1)
    elif timeframe == TimeframeEnum.weekly:
        return now + timedelta(weeks=1)
    else:
        return now + timedelta(days=30)


class PredictionCreate(BaseModel):
    email: str
    name: Optional[str] = None
    image: Optional[str] = None
    asset: AssetEnum
    timeframe: TimeframeEnum
    direction: DirectionEnum


class PredictionOut(BaseModel):
    id: str
    asset: str
    timeframe: str
    direction: str
    price_at_prediction: float
    predicted_at: str
    evaluates_at: str
    result: str

    class Config:
        from_attributes = True


@router.post("", response_model=PredictionOut)
async def create_prediction(body: PredictionCreate, db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(body.email, body.name, body.image, db)

    # 같은 asset+timeframe 중복 예측 방지 (pending 상태인 것)
    existing = await db.execute(
        select(Prediction).where(
            and_(
                Prediction.user_id == user.id,
                Prediction.asset == body.asset,
                Prediction.timeframe == body.timeframe,
                Prediction.result == ResultEnum.pending,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already have a pending prediction for this asset and timeframe")

    # 현재 자산 가격 조회
    price_result = await db.execute(
        select(AssetPriceHistory)
        .where(AssetPriceHistory.symbol == body.asset.value)
        .order_by(AssetPriceHistory.recorded_at.desc())
        .limit(1)
    )
    price_row = price_result.scalar_one_or_none()
    if not price_row:
        raise HTTPException(status_code=503, detail="Price data not available")

    prediction = Prediction(
        id=uuid.uuid4(),
        user_id=user.id,
        asset=body.asset,
        timeframe=body.timeframe,
        direction=body.direction,
        price_at_prediction=price_row.price,
        predicted_at=datetime.now(timezone.utc),
        evaluates_at=evaluates_at_from_timeframe(body.timeframe),
        result=ResultEnum.pending,
    )
    db.add(prediction)
    user.prediction_count += 1
    await db.commit()
    await db.refresh(prediction)

    return PredictionOut(
        id=str(prediction.id),
        asset=prediction.asset.value,
        timeframe=prediction.timeframe.value,
        direction=prediction.direction.value,
        price_at_prediction=prediction.price_at_prediction,
        predicted_at=prediction.predicted_at.isoformat(),
        evaluates_at=prediction.evaluates_at.isoformat(),
        result=prediction.result.value,
    )


@router.get("/me")
async def get_my_predictions(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return {"predictions": [], "stats": {"total": 0, "correct": 0, "accuracy": 0}}

    preds = await db.execute(
        select(Prediction)
        .where(Prediction.user_id == user.id)
        .order_by(Prediction.predicted_at.desc())
        .limit(50)
    )
    predictions = preds.scalars().all()

    accuracy = round(user.correct_count / user.prediction_count * 100) if user.prediction_count > 0 else 0

    return {
        "predictions": [
            {
                "id": str(p.id),
                "asset": p.asset.value,
                "timeframe": p.timeframe.value,
                "direction": p.direction.value,
                "price_at_prediction": p.price_at_prediction,
                "predicted_at": p.predicted_at.isoformat(),
                "evaluates_at": p.evaluates_at.isoformat(),
                "result": p.result.value,
            }
            for p in predictions
        ],
        "stats": {
            "total": user.prediction_count,
            "correct": user.correct_count,
            "accuracy": accuracy,
        },
    }


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    # 커뮤니티 컨센서스: 각 asset+timeframe 조합별 bullish/bearish 비율
    consensus = {}
    for asset in AssetEnum:
        consensus[asset.value] = {}
        for timeframe in TimeframeEnum:
            result = await db.execute(
                select(Prediction.direction, func.count(Prediction.id))
                .where(
                    and_(
                        Prediction.asset == asset,
                        Prediction.timeframe == timeframe,
                        Prediction.result == ResultEnum.pending,
                    )
                )
                .group_by(Prediction.direction)
            )
            rows = result.all()
            total = sum(r[1] for r in rows)
            consensus[asset.value][timeframe.value] = {
                "bullish": next((r[1] for r in rows if r[0] == DirectionEnum.bullish), 0),
                "bearish": next((r[1] for r in rows if r[0] == DirectionEnum.bearish), 0),
                "total": total,
            }

    # 리더보드: 정확도 상위 10명 (최소 5개 예측)
    leaderboard_result = await db.execute(
        select(User)
        .where(User.prediction_count >= 5)
        .order_by((User.correct_count / User.prediction_count).desc())
        .limit(10)
    )
    leaderboard = [
        {
            "name": u.name,
            "image": u.image,
            "total": u.prediction_count,
            "correct": u.correct_count,
            "accuracy": round(u.correct_count / u.prediction_count * 100),
        }
        for u in leaderboard_result.scalars().all()
    ]

    return {"consensus": consensus, "leaderboard": leaderboard}
