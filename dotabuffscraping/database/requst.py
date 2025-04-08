from database.models import async_session
from database.models import Hero, Counter
from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def get_heroes(characteristics):
    async with async_session() as session:
        return await session.scalars(select(Hero).where(Hero.characteristics == characteristics))

async def check_heroes_id(heroes_id):
    async with async_session() as session:
        return await session.scalar(select(Hero).where(Hero.id == heroes_id))

async def counters_heroes(hero):
    async with async_session() as session:
        query = await session.execute(
            select(Hero)
            .options(joinedload(Hero.counters))
            .where(Hero.id == hero)
        )
        result = query.unique().scalar_one_or_none()
        if result:
            return result.counters
        return []

async def get_all_heroes(hero_name):
    async with async_session() as session:
        # тут ищем героя по имени
        current_hero = await session.scalar(select(Hero).where(Hero.name == hero_name))
        # но передаем ток idW
        if current_hero:
            return current_hero.id
        else:
            return True