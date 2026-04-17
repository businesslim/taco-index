"""
초기 30명 인플루언서 데이터 시드.
실행: cd backend && python -m app.influencer.seed
x_user_id는 X API 연동 후 fetcher.get_user_id()로 채워야 함.
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.influencer.models import Influencer

INITIAL_INFLUENCERS = [
    # Investors
    {"handle": "saylor", "name": "Michael Saylor", "category": "Investor", "domain": "crypto"},
    {"handle": "CathieWood", "name": "Cathie Wood", "category": "Investor", "domain": "stock"},
    {"handle": "APompliano", "name": "Anthony Pompliano", "category": "Investor", "domain": "crypto"},
    {"handle": "chamath", "name": "Chamath Palihapitiya", "category": "Investor", "domain": "stock"},
    {"handle": "BillAckman", "name": "Bill Ackman", "category": "Investor", "domain": "stock"},
    {"handle": "mcuban", "name": "Mark Cuban", "category": "Investor", "domain": "stock"},
    {"handle": "ptj", "name": "Paul Tudor Jones", "category": "Investor", "domain": "macro"},
    {"handle": "PeterSchiff", "name": "Peter Schiff", "category": "Investor", "domain": "gold"},
    {"handle": "RaoulGMI", "name": "Raoul Pal", "category": "Investor", "domain": "macro"},
    {"handle": "kevinolearytv", "name": "Kevin O'Leary", "category": "Investor", "domain": "stock"},
    # CEOs
    {"handle": "elonmusk", "name": "Elon Musk", "category": "CEO", "domain": "stock"},
    {"handle": "jack", "name": "Jack Dorsey", "category": "CEO", "domain": "crypto"},
    {"handle": "brian_armstrong", "name": "Brian Armstrong", "category": "CEO", "domain": "crypto"},
    {"handle": "sama", "name": "Sam Altman", "category": "CEO", "domain": "stock"},
    {"handle": "cz_binance", "name": "Changpeng Zhao", "category": "CEO", "domain": "crypto"},
    {"handle": "tyler", "name": "Tyler Winklevoss", "category": "CEO", "domain": "crypto"},
    {"handle": "LarryFink", "name": "Larry Fink", "category": "CEO", "domain": "stock"},
    {"handle": "JamieDimon", "name": "Jamie Dimon", "category": "CEO", "domain": "macro"},
    # Big Tech
    {"handle": "VitalikButerin", "name": "Vitalik Buterin", "category": "BigTech", "domain": "crypto"},
    {"handle": "balajis", "name": "Balaji Srinivasan", "category": "BigTech", "domain": "crypto"},
    {"handle": "naval", "name": "Naval Ravikant", "category": "BigTech", "domain": "stock"},
    {"handle": "nic__carter", "name": "Nic Carter", "category": "BigTech", "domain": "crypto"},
    {"handle": "adam3us", "name": "Adam Back", "category": "BigTech", "domain": "crypto"},
    # Economists
    {"handle": "Nouriel", "name": "Nouriel Roubini", "category": "Economist", "domain": "macro"},
    {"handle": "paulkrugman", "name": "Paul Krugman", "category": "Economist", "domain": "macro"},
    {"handle": "LHSummers", "name": "Larry Summers", "category": "Economist", "domain": "macro"},
    {"handle": "elerianm", "name": "Mohamed El-Erian", "category": "Economist", "domain": "stock"},
    {"handle": "LynAldenContact", "name": "Lyn Alden", "category": "Economist", "domain": "macro"},
    {"handle": "krugermacro", "name": "Alex Krüger", "category": "Economist", "domain": "macro"},
    {"handle": "biancoresearch", "name": "Jim Bianco", "category": "Economist", "domain": "macro"},
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        count = 0
        for data in INITIAL_INFLUENCERS:
            result = await db.execute(
                select(Influencer).where(Influencer.handle == data["handle"])
            )
            if result.scalar_one_or_none() is None:
                db.add(Influencer(**data))
                count += 1
        await db.commit()
    print(f"Seeded {count} influencers ({len(INITIAL_INFLUENCERS)} total in list)")


if __name__ == "__main__":
    asyncio.run(seed())
