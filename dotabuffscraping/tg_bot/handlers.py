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
from database.requst import check_heroes_id, get_all_heroes, chech_many_counters_heroes

router = Router()

# Состояния 
class Write_hero(StatesGroup):
    Write_Hero = State() # Для hero 
    Select_heroes = State() # Для menu

class Base_Command():
    @router.message(CommandStart())
    async def command_start_handler(message: Message):
        await message.answer("Добро пожаловать!\nЭто бот для анализа статистики героев из сайта дотабафф для Дота2\nНапишите команду /menu для начала\n/hero")
    # Иди нахуй
    @router.message(Command("help"))
    async def command_help(message: Message):
        await message.answer("Иди нахуй\n/menu")

    # Команда для админ меню
    @router.message(Command("Admin"))
    async def user_id(message: Message):
        if message.from_user.id == int(getenv("ADMIN_ID")): # проверка с файла .env являеться ли пользователь админом
            await message.answer("Вы зашли как администратор что вы хотитте зделать", reply_markup=admin_keyboard) # кнопка админ меню

    # тут мы начинам парсинг если нажали кнопку в админ меню
    @router.callback_query(F.data.startswith("start_scraping"))
    async def scraping(callback: CallbackQuery):
        await callback.answer("")
        await callback.message.edit_text("Вы начали парсинг dotabuff")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Хуйня для винды
        await async_main() #Создаем таблицу
        await main() # Парсим дотабафф

class hero_Command():
    @router.message(Command("hero"))
    async def command_heroes(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Write_Hero)
        await message.answer("Напишите имя вашего героя(на английском)")


    @router.message(Write_hero.Write_Hero)
    async def write_h(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(Write_hero.Select_heroes)
        await state.update_data(name=message.text.lower(), all_counters=[])
        data = await state.get_data() # Возрощает словарь
        data_id = await get_all_heroes(data["name"])  # запускаем функцию
        if data_id == True:
            await message.answer("Этого героя не сущиствует попробуйте еще раз")
            return
        else:
            top_counters, worst_counters, all_counters  = await chech_many_counters_heroes([data_id.id]) # тут запускаем функцию 
            await state.update_data(all_counters=all_counters)
            text = f"Контрпики для {data["name"]}:\n\n"
            for top_counter in top_counters:        # перебираем кортеж
                text += f"{top_counter[0]}: {top_counter[1]}\n"
            text += f"\nПять худших герояв против {data["name"]}:\n"
            for worst_counter in worst_counters:
                text += f"{worst_counter[0]}: {worst_counter[1]}\n"
            await message.answer(text, reply_markup= await more_info_heroes(characteristics=data_id.characteristics)) # тут функцию для клавы

    # Копипаст
    @router.callback_query(Write_hero.Write_Hero, F.data.startswith("moreheroinfo_"))
    async def more_info_analytic(callback: CallbackQuery, state: FSMContext):
        characteristic = callback.data.split("_")[2]
        data = await state.get_data()
        all_counters = data.get("all_counters", [])
        text = f"Контрпики для ваших героев:\n\n"
        for all_counter in all_counters:
            text += f"{all_counter[0]}:{all_counter[1]}\n"
        await callback.answer("")
        await callback.message.edit_text(text, reply_markup= await back_her(characteristic))
        await state.update_data(all_counters=[])

class menu_Command():
    # команда меню
    @router.message(Command("menu"))
    async def start_selection(message:Message, state: FSMContext):
        # Очищаем другие состояния и устанавливаем новое
        await state.clear()
        await state.set_state(Write_hero.Select_heroes)
        # Создаем в дате 3 списка
        await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[])
        await message.answer("Выбирите категорию героев для анализа", reply_markup=characteristics_list) # Вызываем клавиатуру характеристик
    # ето возращает к характеристикам
    @router.callback_query(F.data.startswith("home"))
    async def command_heroes(callback: CallbackQuery):
        await callback.answer("")
        await callback.message.edit_text("Выберите категорию вашего героя", reply_markup=characteristics_list)

    # кнопки героев при нажатии на характеристику
    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("chara_"))
    async def analis_characteristic(callback: CallbackQuery, state: FSMContext):
        # Получаем характеристику
        characteristic = callback.data.split("_")[1]
        # Надо ли удалять прошлих героев ?
        delete_data = callback.data.split("_")[2]
        if delete_data == "True":
            await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[])
        # Получаем дату
        data = await state.get_data()
        # Получаем выбраных героев
        selectes_heroes = data.get("selectes_heroes", [])
        await callback.answer("")
        text = f"Выбирете героев\nВыбраные герои\n"
        for select_her in selectes_heroes: # и проходимся по ним
            text += f"{select_her}\n"
        if selectes_heroes: # если он есть то добавляем кнопку снизу
            await callback.message.edit_text(text, reply_markup= await heroes(characteristic, ready_button=True)) # вызываем функцию с выводом героев
        else:
            await callback.message.edit_text(text, reply_markup= await heroes(characteristic, ready_button=False))

    # обработка кнопки героя
    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("heroes_"))
    async def analis_heroes(callback: CallbackQuery, state: FSMContext):
        # ищем таблицу героя по ид
        hero = await check_heroes_id(int(callback.data.split("_")[1]))
        data = await state.get_data()
        # получаем с даты heroes and id
        selectes_heroes = data.get("selectes_heroes", [])
        selectes_heroes_id = data.get("selectes_heroes_id", [])
        # если нету выбраного героя то
        if hero.id not in selectes_heroes_id:
            # добавляем к нему новые id и наме
            selectes_heroes.append(hero.name)
            selectes_heroes_id.append(hero.id)
            # и сохраняем в дату
            await state.update_data(selectes_heroes=selectes_heroes)
            await state.update_data(selectes_heroes_id=selectes_heroes_id)
        else: # а если есть
            await callback.message.answer("Вы хотели выбрать 1 героя 2 раза пожалуйста выбирите другого героя", reply_markup= await heroes(hero.characteristics, ready_button=True))
            return
        if len(selectes_heroes) >= 5: #Если выбраных героев больше 5 то
            counters, worst_counters, all_counters = await chech_many_counters_heroes(selectes_heroes_id) # выполняем функцию
            # обновляем дату про всех героив
            await state.update_data(all_counters=all_counters)
            text = f"Лучшие герои\n"
            for counter in counters: # перебираем 
                text += f"{counter[0]}:{counter[1]}\n"
            text += f"\nХудшие герои:\n"
            for worst_counter in worst_counters:
                text += f"{worst_counter[0]}:{worst_counter[1]}\n"
            await callback.message.edit_text(text, reply_markup= await more_info_heroes(hero.characteristics)) # и выводим
        else: #Если выбраных героев меньше то
            text = f"Выбирете героев\nВыбрано:"
            for selectes_her in selectes_heroes: # тут перебираем всех выбраных героев
                text += f"{selectes_her}\n" # записуем в text 
            await callback.answer("")
            await callback.message.edit_text(text, reply_markup= await heroes(hero.characteristics, ready_button=True)) # и выводим и повторяем

    # тут тоже самое что и здесь if len(selectes_heroes) >= 5
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
      
    # хендер который розкрывает все контрпики
    @router.callback_query(Write_hero.Select_heroes, F.data.startswith("moreheroinfo_"))
    async def more_info_analytic(callback: CallbackQuery, state: FSMContext):
        characteristic = callback.data.split("_")[1]
        data = await state.get_data()
        all_counters = data.get("all_counters", []) # Достаем все контрпики с дати
        text = f"Контрпики для ваших героев:\n\n"
        for all_counter in all_counters:
            text += f"{all_counter[0]}:{all_counter[1]}\n"
        await callback.answer("")
        await callback.message.edit_text(text, reply_markup= await back_her(characteristic))
        await state.update_data(selectes_heroes=[], selectes_heroes_id=[], all_counters=[]) # в конце чистим всю дату

    # кнопка перемещения
    @router.callback_query(F.data.startswith("navigation_"))
    async def navigation(callback: CallbackQuery, state: CallbackQuery):
#получаем с калбака характеристики страницу и максимальное количество станиц
        navigation, characteristics, page, max_page = callback.data.split("_")
        if int(page) < 0: # если мы на 1 странице назад
            return
        elif int(page) >= int(max_page): # если мы на последней странице идем вперед
            return
        else:
            data = await state.get_data()
            selectes_heroes = data.get("selectes_heroes", [])
            text = f"Выбирете героев\nВыбраные герои\n"
            for select_her in selectes_heroes:
                text += f"{select_her}\n" # все что с даты все надо для вывода наданный момент выбраных герояв
            await callback.answer("")
            if selectes_heroes: # если есть выбраные герои то reply_markup с кнопкой готовности ready_button
                await callback.message.edit_text(text, reply_markup= await heroes(characteristics, int(page),ready_button=True)) 
            else:  # если у нас нету выбраных героев то reply_markup без кнопки готовности ready_button
                await callback.message.edit_text(text, reply_markup= await heroes(characteristics, int(page),ready_button=False))
