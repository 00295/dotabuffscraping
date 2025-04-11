from collections import defaultdict
from database.models import async_session
from database.models import Hero, Counter
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


async def get_heroes(characteristics):
    async with async_session() as session:
        # возращаем всех героев нужной характеристики
        return await session.scalars(select(Hero).where(Hero.characteristics == characteristics))

# ищем таблицу героя по ид
async def check_heroes_id(heroes_id):
    async with async_session() as session:
        return await session.scalar(select(Hero).where(Hero.id == heroes_id))


# Функция которая находит и возращает контрики 
async def chech_many_counters_heroes(hero_ids): # Принимает их айдишники
    async with async_session() as session:
        query = await session.execute(
            select(Counter).where(Counter.hero_id.in_(hero_ids))
        )

        all_counters = query.scalars().all() # all превращает в список

        query_names = await session.execute(
            select(Hero.name).where(Hero.id.in_(hero_ids))
        )


        select_heroes = set(query_names.scalars().all())
    
    # создаем лист
    counter_stats = defaultdict(list)
    for counter in all_counters:
        # Если контрпикпик есть в списке выбраних герояв то скип если нет то:
        if counter.counter_name.replace(" ", "-").lower() not in select_heroes:
            # В лист записываем как key имя героя и книму значение position
            counter_stats[counter.counter_name].append(float(counter.position))
    # counter_stats = {("Viper", [1.2, 0.1,-0.6, 2.1]), ("Sniper", [1.0, 0.1,-0.6, 2.1])}
    avg_position = {
        # имя героя тут мы добовляем position тут цикл просто дял удобства в 1 строку записал
        name: round(sum(values),2) for name, values in counter_stats.items()
    }
    # avg_position = {"Viper": 1.2, "Sniper": 2.1}
    # avg_position.items() превращает словарь в список кортежей вида (key, value)

    #сортируем                   # тут мы берем выбираем 2елемент кортежа тоесть value и сартируем по убыванию
    count = sorted(avg_position.items(), key=lambda x: x[1], reverse=True)
    # тут просто берем 5 обектов с самым высоким зачение там знизу тоже самое только с самым худшими
    best_counters = sorted(avg_position.items(), key=lambda x: x[1], reverse=True)[:5]
    worst_counters = sorted(avg_position.items(), key=lambda x: x[1], reverse=False)[:5]
    # и возращаем ето
    return best_counters, worst_counters, count


# тут мы ищем героя по имени
async def get_all_heroes(hero_name):
    async with async_session() as session:
        # тут ищем героя по имени
        current_hero = await session.scalar(select(Hero).where(Hero.name == hero_name))
        if current_hero:
            return current_hero
        else:
            return True # если его нет возращаем тру
        
        