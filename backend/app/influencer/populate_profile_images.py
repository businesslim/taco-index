"""
X API에서 인플루언서별 profile_image_url을 조회해 DB에 업데이트.

실행:
    cd backend && python -m app.influencer.populate_profile_images

profile_image_url이 이미 채워진 인플루언서는 건너뜀.
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
            select(Influencer).where(Influencer.profile_image_url == None)  # noqa: E711
        )
        influencers = result.scalars().all()

    logger.info(f"{len(influencers)}명의 profile_image_url 조회 시작...")

    ok, skip = 0, 0
    for inf in influencers:
        try:
            url = await fetcher.get_profile_image_url(inf.handle)
            async with AsyncSessionLocal() as db:
                row = await db.get(Influencer, inf.id)
                if row:
                    row.profile_image_url = url
                    await db.commit()
            logger.info(f"  ✓ @{inf.handle}")
            ok += 1
        except Exception as e:
            logger.warning(f"  ✗ @{inf.handle} 실패: {e}")
            skip += 1

    logger.info(f"\n완료: {ok}명 업데이트, {skip}명 실패")


if __name__ == "__main__":
    asyncio.run(populate())
