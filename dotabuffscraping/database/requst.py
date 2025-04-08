from database.models import async_session
from database.models import Hero, Counter
from sqlalchemy import select


async def get_heroes(characteristics):
    async with async_session() as session:
        return await session.scalars(select(Hero).where(Hero.characteristics == characteristics))

async def check_heroes_id(heroes_id):
    async with async_session() as session:
        return await session.scalar(select(Hero).where(Hero.id == heroes_id))