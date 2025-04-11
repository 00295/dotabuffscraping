from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requst import get_heroes

size_pages = 9

characteristics_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сила", callback_data="chara_Сила_")],
    [InlineKeyboardButton(text="Ловкость", callback_data="chara_Ловкость_")],
    [InlineKeyboardButton(text="Интелект", callback_data="chara_Интеллект_")],
    [InlineKeyboardButton(text="Универсальный",callback_data="chara_Универсальные_")],
    ])

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обновить базу данных", callback_data="start_scraping")]
    ])

            #Характеристику текущую страницу(равно 0 если ничего не передано) и нужна ли кнопка снизу
async def heroes(characteristics, page: int = 0, ready_button: bool = False):
    # Тут мы получаем всех героив выбраной характеристики 
    all_heroes = (await get_heroes(characteristics)).all()
    # билдер
    builder = InlineKeyboardBuilder()
# общеэ количество нужных нам страниц  округляет в большую сторону
    total_pages = (len(all_heroes) + size_pages - 1) // size_pages

    # ищем первого героя каждой страници а снизу последнего
    first_heroes_id_current_page = page * size_pages
    last_heroes_id_current_page = first_heroes_id_current_page + size_pages
    # тут выбираем айдишники имено на етой стнарницы
    heroes_on_page = all_heroes[first_heroes_id_current_page:last_heroes_id_current_page]

    for heroes in heroes_on_page: # А тут мы ето перебираем и создаем кнопку с callback_data во 2 части передаем афдишник
        builder.add(InlineKeyboardButton(text=heroes.name, callback_data=f"heroes_{heroes.id}"))
    # создаем кнопку назад в калбак 3 обект передаем новую страницу 
    builder.add(InlineKeyboardButton(text="<<<<", callback_data=f"navigation_{characteristics}_{page - 1}_{total_pages}"))
    # ето кнопка возрощения на выбор характеристики
    builder.add(InlineKeyboardButton(text="Home", callback_data="home"))
    # создаем кнопку вперед в калбак 3 обект передаем новую страницу 
    builder.add(InlineKeyboardButton(text=">>>>", callback_data=f"navigation_{characteristics}_{page + 1}_{total_pages}"))
    # если мы показали что надо создаем кнопку готовности
    if ready_button == True:
        builder.add(InlineKeyboardButton(text="Готово", callback_data=f"ready_alanytics_{characteristics}"))
    # и создаем таблицу
    return builder.adjust(3).as_markup()


async def more_info_heroes(characteristics):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Посмотреть все контрпики", callback_data=f"moreheroinfo_{characteristics}"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"chara_{characteristics}_True"))
    return builder.adjust(1).as_markup()

async def back_her(characteristics):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"chara_{characteristics}_"))
    return builder.adjust(1).as_markup()
