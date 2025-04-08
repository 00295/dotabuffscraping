from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards import characteristics_list, heroes
from database.requst import check_heroes_id, counters_heroes, get_all_heroes

router = Router()

class Write_hero(StatesGroup):
    Write_Hero = State()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Добро пожаловать!\nЭто бот для анализа статистики героев из сайта дотабафф для Дота2\nОсновные команды:\n/Heroes\n/hero")

@router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.answer("Основные команды:")

@router.message(Command("Heroes"))
async def command_heroes(message: Message):
    await message.answer("Выберите категорию вашего героя", reply_markup=characteristics_list)

@router.message(Command("hero"))
async def command_heroes(message: Message, state: FSMContext):
    await state.set_state(Write_hero.Write_Hero)
    await message.answer("Напишите имя вашего героя(на английском)")


@router.message(Write_hero.Write_Hero)
async def write_h(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    data_id = await get_all_heroes(data["name"])
    if data_id == True:
        await message.answer("Етого героя не сущиствует попробуйте еще раз")
        return
    else:
        counter_heroes = await counters_heroes(data_id)
        text = f"Контрпики для {data["name"]}:\n\n"
        for counter_heroe in counter_heroes:
            text += f"{counter_heroe.counter_name}: {counter_heroe.position}\n"
        await message.answer(text)
    await state.clear()

@router.callback_query(F.data.startswith("chara_"))
async def strength_heroes_list(callback: CallbackQuery):
    characteristic = callback.data.split("_")[1]
    await callback.answer("")
    await callback.message.edit_text("Выбирете героя", reply_markup= await heroes(characteristic))

@router.callback_query(F.data.startswith("heroes_"))
async def hero(callback: CallbackQuery):
    hero = await check_heroes_id(int(callback.data.split("_")[1]))
    counter_heroes = await counters_heroes(hero.id)
    text = f"Контрпики для {hero.name}:\n\n"
    for counter_heroe in counter_heroes:
        text += f"{counter_heroe.counter_name}: {counter_heroe.position}\n"
    await callback.message.answer(text)

