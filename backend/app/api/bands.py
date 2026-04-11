from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.index import IndexBand
from app.schemas.index import BandSchema

router = APIRouter(prefix="/api/bands", tags=["bands"])

@router.get("", response_model=list[BandSchema])
async def get_bands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IndexBand).order_by(IndexBand.min_score))
    return result.scalars().all()
