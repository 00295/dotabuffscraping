import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, ForeignKey, select
from database.models import async_session, async_main, Counter, Hero

# количество потоков
sem = asyncio.Semaphore(5)


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
BASE_URL = "https://ru.dotabuff.com"

# Удобная функция что бы каждый раз не прописовать код внутри
async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()


async def parse_hero_links(session):
    # Заранее создаем список
    hero_urls = []
    html = await fetch(session, f"{BASE_URL}/heroes")
    soup = BeautifulSoup(html, "lxml")
    # ищем
    dotabuff_statics_main_menu = soup.find_all(class_="tw-max-w-full")
    # перебераем что нашли
    for dotabuff_static_ in dotabuff_statics_main_menu:
        # ище ищем
        characteristics = dotabuff_static_.find(class_="tw-mb-3")
        # выбираем ток текст
        characteristic = characteristics.text.strip()
        hero_url = dotabuff_static_.find_all(class_="tw-group tw-relative tw-block tw-aspect-video tw-w-full tw-rounded-sm tw-bg-background tw-shadow-sm tw-shadow-black/20 tw-transition-transform tw-duration-100 hover:tw-z-10 hover:tw-scale-150")
        # записываем все в список и возрощаем в конце
        for url in hero_url:
            hero_urls.append((url,characteristic))

    return hero_urls


async def parse_counters(session, hero_url, db_session):
    # Коректируем имя героя
    hero_url_original, characteristic = hero_url
    hero_name = hero_url_original.text.lower().replace(' ',  '-')
    # его юрл
    counters_url = f"{BASE_URL}/heroes/{hero_name}/counters"
    #Есть ли герой в базе данных
    hero = await db_session.scalar(select(Hero).where(Hero.name == hero_name))
    # Если нету то записываем
    if not hero:
        hero = Hero(name=hero_name, characteristics=characteristic)
        db_session.add(hero)
        await db_session.flush()

    html = await fetch(session, counters_url)
    soup = BeautifulSoup(html, "lxml")

    # ищем в Url нужный клас
    counter_names = soup.find(class_="sortable")
    # Если его нету то выводим про ето в терминал
    if not counter_names:
        print(f"[!] Таблица не найдена на странице: {counters_url}")
        return
    # тоже самое но с тбоди
    tbody = counter_names.find("tbody")
    if not tbody:
        print(f"[!] tbody не найден на странице: {counters_url}")
        return
    # Ищем в тбоди все тр обекти
    rows = tbody.find_all("tr")
    # проходим по ним с помощу цикла
    for row in rows:
        # Ищем в нем все td
        cells = row.find_all("td")
        # обращаемся к нужным td
        name_cells = cells[1]
        position_cells = cells[2]

        # strip()убирает не нужные пробелы и записываем имя героя
        counter_names = name_cells.text.strip()
        # Получаем цифри сили контрпика и записываем
        position = position_cells.get("data-value", "").strip()
        #print(counter_names)
        if not counter_names or not position:
            continue
        # Добавляем в базу данных hero.id так как при каждом вызовом функции он миняеться остальное росписано выше
        db_session.add(Counter(hero_id=hero.id, counter_name=counter_names, position=position))

    await db_session.commit()
    print(f"Собрано для героя: {hero_name}")

# Основная функция
async def main():
    async with aiohttp.ClientSession() as session:
        # вызываем функция что возрощает список героев
        hero_urls = await parse_hero_links(session)

        # Функция-обёртка, создающая отдельную сессию БД
        async def process_hero(url):
            # Ограничивает количество потоков
            async with sem:
                async with async_session() as db_session:
                    await parse_counters(session, url, db_session)
        # Создаем задачи внутри цикл и передает имя героя
        tasks = [process_hero(url) for url in hero_urls]
        # Выполняет задачи
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(async_main())
    asyncio.run(main())