from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requst import get_heroes

list_heroes_name = []

characteristics_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сила", callback_data="Сила")],
    [InlineKeyboardButton(text="Ловкость", callback_data="Ловкость")],
    [InlineKeyboardButton(text="Интелект", callback_data="Интеллект")],
    [InlineKeyboardButton(text="Унмверсальный",callback_data="Универсальные")],
    ])

async def heroes(characteristics):
    all_heroes = await get_heroes(characteristics)
    builder = InlineKeyboardBuilder()
    for heroes in all_heroes:
        list_heroes_name.append(heroes.name)
        builder.add(InlineKeyboardButton(text=heroes.name, callback_data=f"heroes_{heroes.id}"))
    return builder.adjust(3).as_markup()
