import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from scraping_dotabuff.scraping import main
from database.models import async_main
from tg_bot.handlers import router


async def run_bot():
    load_dotenv()
    bot = Bot(token=getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())