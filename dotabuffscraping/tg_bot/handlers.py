from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from tg_bot.keyboards import characteristics_list, heroes
from database.requst import check_heroes_id

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Добро пожаловать!\nЭто бот для анализа статистики героев из сайта дотабафф для Дота2\nОсновные команды:\n/Heroes")

@router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.answer("Основные команды:")

@router.message(Command("Heroes"))
async def command_heroes(message: Message):
    await message.answer("Выберите категорию вашего героя", reply_markup=characteristics_list)

@router.callback_query(F.data.startswith("Сила"))
async def strength_heroes_list(callback: CallbackQuery):
    await callback.message.answer("Выбирете героя", reply_markup= await heroes(callback.data))

@router.callback_query(F.data.startswith("Ловкость"))
async def strength_heroes_list(callback: CallbackQuery):
    await callback.message.answer("Выбирете героя", reply_markup= await heroes(callback.data))

@router.callback_query(F.data.startswith("Интеллект"))
async def strength_heroes_list(callback: CallbackQuery):
    await callback.message.answer("Выбирете героя", reply_markup= await heroes(callback.data))

@router.callback_query(F.data.startswith("Универсальные"))
async def strength_heroes_list(callback: CallbackQuery):
    await callback.message.answer("Выбирете героя", reply_markup= await heroes(callback.data))

@router.callback_query(F.data.startswith("heroes_"))
async def hero(callback: CallbackQuery):
    hero = await check_heroes_id(int(callback.data.split("_")[1]))

