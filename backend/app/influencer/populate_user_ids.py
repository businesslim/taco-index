"""
X API에서 인플루언서별 x_user_id를 조회해 DB에 업데이트.

실행 (시드 후 1회):
    cd backend && python -m app.influencer.populate_user_ids

X_BEARER_TOKEN 환경변수가 설정돼 있어야 함.
실패한 핸들은 건너뛰고 로그에 출력.
"""
import asyncio
import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.influencer.models import Influencer
from app.influencer.fetcher import XApiFetcher

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def populate() -> None:
    fetcher = XApiFetcher()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Influencer).where(Influencer.x_user_id == None)  # noqa: E711
        )
        influencers = result.scalars().all()

    logger.info(f"{len(influencers)}명의 x_user_id 조회 시작...")

    ok, skip = 0, 0
    for inf in influencers:
        try:
            user_id = await fetcher.get_user_id(inf.handle)
            async with AsyncSessionLocal() as db:
                row = await db.get(Influencer, inf.id)
                if row:
                    row.x_user_id = user_id
                    await db.commit()
            logger.info(f"  ✓ @{inf.handle} → {user_id}")
            ok += 1
        except Exception as e:
            logger.warning(f"  ✗ @{inf.handle} 실패: {e}")
            skip += 1

    logger.info(f"\n완료: {ok}명 업데이트, {skip}명 실패")
    if skip:
        logger.info("실패한 핸들은 수동으로 x_user_id를 채워주세요.")


if __name__ == "__main__":
    asyncio.run(populate())
