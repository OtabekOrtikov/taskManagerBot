from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME
from database.db_utils import get_user, get_db_pool
from btns import back_to_main

async def show_referal_links(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    async with db_pool.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        if user['role_id'] == 1:
            departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1", user['company_id'])
        else:
            departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1 AND id = $2", user['company_id'], user['department_id'])

    text = f"Список реферальных ссылок для компании ‘**{company['company_name']}**’:" if user['lang'] == 'ru' else f"‘**{company['company_name']}**’ kompaniyasining referal havolalari ro‘yxati:"
    keyboard = []

    if lang == 'ru':
        for department in departments:
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company['id']}_department={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Парни, заходите по ссылке ниже, чтобы получить задание от начальника."
            keyboard.append([InlineKeyboardButton(text=f"Отдел: {department['department_name']}", url=share_link)])

    elif lang == 'uz':
        for department in departments:
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company['id']}_department={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Yigitlar, boshliqdan vazifa olish uchun quyidagi havolaga kiring."
            keyboard.append([InlineKeyboardButton(text=f"Bo'lim: {department['department_name']}", url=share_link)])
    
    keyboard.append([back_to_main[lang]])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="Markdown")
    await state.update_data(main_menu_message_id=callback.message.message_id)