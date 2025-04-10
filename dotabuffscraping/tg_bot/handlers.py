import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from scraping_dotabuff.scraping import main
from database.models import async_main

from tg_bot.keyboards import characteristics_list, heroes, admin_keyboard, more_info_heroes, back_her
from database.requst import check_heroes_id, check_counters_heroes, get_all_heroes, chech_many_counters_heroes

router = Router()

class Write_hero(StatesGroup):
    Write_Hero = State()
    Heroes_Comand_Heroes = State()
    Select_heroes = State()

class Base_Command():
    @router.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        await message.answer("Добро пожаловать!\nЭто бот для анализа статистики героев из сайта дотабафф для Дота2\nОсновные команды:\n/Heroes\n/hero\n/analis")

    @router.message(Command("help"))
    async def command_help(message: Message) -> None:
        await message.answer("Основные команды:")

    @router.message(Command("Admin"))
    async def user_id(message: Message):
        if message.from_user.id == int(getenv("ADMIN_ID")):
            await message.answer("Вы зашли как администратор что вы хотитте зделать", reply_markup=admin_keyboard)

    @router.callback_query(F.data.startswith("start_scraping"))
    async def scraping(callback: CallbackQuery):
        await callback.answer("")
        await callback.message.edit_text("Вы начали парсинг dotabuff")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        await async_main()
        await main()

class Hero_Button_Command():
    @router.message(Command("Heroes"))
    async def command_heroes(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Heroes_Comand_Heroes)
        await message.answer("Выберите категорию вашего героя", reply_markup=characteristics_list)

    @router.callback_query(F.data.startswith("home"))
    async def command_heroes(callback: CallbackQuery):
        await callback.answer("")
        await callback.message.edit_text("Выберите категорию вашего героя", reply_markup=characteristics_list)

    @router.callback_query(F.data.startswith("chara_"), Write_hero.Heroes_Comand_Heroes)
    async def strength_heroes_list(callback: CallbackQuery):
        characteristic = callback.data.split("_")[1]
        await callback.answer("")
        await callback.message.edit_text("Выбирете героя", reply_markup= await heroes(characteristic))

    @router.callback_query(F.data.startswith("charadelete_"), Write_hero.Heroes_Comand_Heroes)
    async def strength_heroes_list(callback: CallbackQuery):
        characteristic = callback.data.split("_")[1]
        await callback.answer("")
        await callback.message.edit_text("Выбирете героя", reply_markup= await heroes(characteristic))

    @router.callback_query(Write_hero.Heroes_Comand_Heroes, F.data.startswith("heroes_"))
    async def hero(callback: CallbackQuery):
        hero = await check_heroes_id(int(callback.data.split("_")[1]))
        top_counters, worst_counters = await check_counters_heroes(hero.id, full_check=False)
        text = f"Пять лучших герояв против {hero.name}:\n"
        for top_counter in top_counters:
            text += f"{top_counter.counter_name}: {top_counter.position}\n"
        text += f"\nПять худших герояв против {hero.name}:\n"
        for worst_counter in worst_counters:
            text += f"{worst_counter.counter_name}: {worst_counter.position}\n"
        await callback.answer("")
        await callback.message.edit_text(text, reply_markup= await more_info_heroes(characteristics=hero.characteristics, hero=hero.id))

    @router.callback_query(Write_hero.Heroes_Comand_Heroes, F.data.startswith("moreheroinfo_"))
    async def more_info_hero(callback: CallbackQuery):
        hero = await check_heroes_id(int(callback.data.split("_")[1]))
        counters_heroes = await check_counters_heroes(hero.id, full_check=True)
        text = f"Контрпики для {hero.name}:\n\n"
        for counter_heroe in counters_heroes:
            text += f"{counter_heroe.counter_name}: {counter_heroe.position}\n"
        await callback.answer("")
        await callback.message.edit_text(text, reply_markup=await back_her(hero.characteristics))

    @router.callback_query(F.data.startswith("navigation_"))
    async def navigation(callback: CallbackQuery):
        nav, characteristics, page = callback.data.split("_")
        if int(page) < 0:
            return
        else:
            await callback.answer("")
            await callback.message.edit_text("Выбирете героя", reply_markup= await heroes(characteristics, int(page)))

class hero_Command():
    @router.message(Command("hero"))
    async def command_heroes(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Write_Hero)
        await message.answer("Напишите имя вашего героя(на английском)")


    @router.message(Write_hero.Write_Hero)
    async def write_h(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Heroes_Comand_Heroes)
        await state.update_data(name=message.text)
        data = await state.get_data()
        data_id = await get_all_heroes(data["name"])
        if data_id == True:
            await message.answer("Этого героя не сущиствует попробуйте еще раз")
            return
        else:
            top_counters, worst_counters  = await check_counters_heroes(data_id.id, full_check=False)
            text = f"Контрпики для {data["name"]}:\n\n"
            for top_counter in top_counters:
                text += f"{top_counter.counter_name}: {top_counter.position}\n"
            text += f"\nПять худших герояв против {data["name"]}:\n"
            for worst_counter in worst_counters:
                text += f"{worst_counter.counter_name}: {worst_counter.position}\n"
            await message.answer(text, reply_markup= await more_info_heroes(characteristics=data_id.characteristics, hero=data_id.id))

class analis_Command():
    @router.message(Command("analis"))
    async def start_selection(message:Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Select_heroes)
        await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[])
        await message.answer("Выбирите категорию героев для анализа", reply_markup=characteristics_list)

    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("chara_"))
    async def analis_characteristic(callback: CallbackQuery, state: FSMContext):
        characteristic = callback.data.split("_")[1]
        await callback.answer("")
        await callback.message.edit_text("Выбирете героев", reply_markup= await heroes(characteristic))

    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("charadelete_"))
    async def analis_characteristic(callback: CallbackQuery, state: FSMContext):
        await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[])
        characteristic = callback.data.split("_")[1]
        await callback.answer("")
        await callback.message.edit_text("Выбирете героев", reply_markup= await heroes(characteristic))

    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("heroes_"))
    async def analis_heroes(callback: CallbackQuery, state: FSMContext):
        hero = await check_heroes_id(int(callback.data.split("_")[1]))
        data = await state.get_data()
        selectes_heroes = data.get("selectes_heroes", [])
        selectes_heroes_id = data.get("selectes_heroes_id", [])
        if hero.id not in selectes_heroes_id:
            selectes_heroes.append(hero.name)
            selectes_heroes_id.append(hero.id)
            await state.update_data(selectes_heroes=selectes_heroes)
            await state.update_data(selectes_heroes_id=selectes_heroes_id)
        else:
            await callback.message.answer("Вы хотели выбрать 1 героя 2 раза пожалуйста выбирите другого героя", reply_markup= await heroes(hero.characteristics, ready_button=True))
            return
        if len(selectes_heroes) >= 5:
            counters, worst_counters, all_counters = await chech_many_counters_heroes(selectes_heroes_id)
            await state.update_data(all_counters=all_counters)
            text = f"Лучшие герои\n"
            for counter in counters:
                text += f"{counter[0]}:{counter[1]}\n"
            text += f"\nХудшие герои:\n"
            for worst_counter in worst_counters:
                text += f"{worst_counter[0]}:{worst_counter[1]}\n"
            await callback.message.edit_text(text, reply_markup= await more_info_heroes(hero.characteristics, hero.name))
        else:
            text = f"Выбирете героев\nВыбрано:"
            for selectes_her in selectes_heroes:
                text += f"{selectes_her}\n"
            await callback.answer("")
            await callback.message.edit_text(text, reply_markup= await heroes(hero.characteristics, ready_button=True))


    @router.callback_query(F.data.startswith("ready_alanytics"))
    async def ready_button(callback : CallbackQuery, state: FSMContext):
        characteristic = callback.data.split("_")[2]
        data = await state.get_data()
        selectes_heroes = data.get("selectes_heroes", [])
        selectes_heroes_id = data.get("selectes_heroes_id", [])
        counters, worst_counters, all_counters = await chech_many_counters_heroes(selectes_heroes_id)
        await state.update_data(all_counters=all_counters)
        text = f"Лучшие герои\n"
        for counter in counters:
            text += f"{counter[0]}:{counter[1]}\n"
        text += f"\nХудшие герои:\n"
        for worst_counter in worst_counters:
            text += f"{worst_counter[0]}:{worst_counter[1]}\n"
        await callback.message.edit_text(text, reply_markup= await more_info_heroes(characteristic))
      

    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("moreheroinfo_"))
    async def more_info_analytic(callback: CallbackQuery, state: FSMContext):
        characteristic = callback.data.split("_")[2]
        data = await state.get_data()
        all_counters = data.get("all_counters", [])
        text = f"Контрпики для ваших героев:\n\n"
        for all_counter in all_counters:
            text += f"{all_counter[0]}:{all_counter[1]}\n"
        await callback.answer("")
        await callback.message.edit_text(text, reply_markup= await back_her(characteristic))
        await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[])
