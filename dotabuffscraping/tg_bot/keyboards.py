from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requst import get_heroes



size_pages = 9
list_heroes_name = []

characteristics_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сила", callback_data="chara_Сила")],
    [InlineKeyboardButton(text="Ловкость", callback_data="chara_Ловкость")],
    [InlineKeyboardButton(text="Интелект", callback_data="chara_Интеллект")],
    [InlineKeyboardButton(text="Универсальный",callback_data="chara_Универсальные")],
    ])

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обновить базу данных", callback_data="start_scraping")]
    ])


async def heroes(characteristics, page: int = 0, ready_button: bool = False):
    all_heroes = (await get_heroes(characteristics)).all()
    builder = InlineKeyboardBuilder()
    total_pages = (len(all_heroes) + size_pages - 1) // size_pages

    first_heroes_id_current_page = page * size_pages
    last_heroes_id_current_page = first_heroes_id_current_page + size_pages
    heroes_on_page = all_heroes[first_heroes_id_current_page:last_heroes_id_current_page]

    for heroes in heroes_on_page:
        builder.add(InlineKeyboardButton(text=heroes.name, callback_data=f"heroes_{heroes.id}"))
    builder.add(InlineKeyboardButton(text="<<<<", callback_data=f"navigation_{characteristics}_{page - 1}"))
    builder.add(InlineKeyboardButton(text="Home", callback_data="home"))
    if page < total_pages - 1:
        builder.add(InlineKeyboardButton(text=">>>>", callback_data=f"navigation_{characteristics}_{page + 1}"))
    if ready_button == True:
        builder.add(InlineKeyboardButton(text="Готово", callback_data=f"ready_alanytics_{characteristics}"))
    return builder.adjust(3).as_markup()


async def more_info_heroes(characteristics, hero: str = "Null"):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Посмотреть все контрпики", callback_data=f"moreheroinfo_{hero}_{characteristics}"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"charadelete_{characteristics}"))
    return builder.adjust(1).as_markup()

async def back_her(characteristics):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"chara_{characteristics}"))
    return builder.adjust(1).as_markup()
