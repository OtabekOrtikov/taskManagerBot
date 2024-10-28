from aiogram.fsm.context import FSMContext
from btns import back_to_settings
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import CompanyChanges
from aiogram.types import InlineKeyboardMarkup
from aiogram import types

async def edit_company_name(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    text = "Enter the new company name:" if lang == 'en' else "Введите новое название компании:" if lang == 'ru' else "Yangi kompaniya nomini kiriting:"

    keyboard = [
        [back_to_settings[lang]]
    ]
    send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(CompanyChanges.company_name)

async def changing_company_name(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    company_name = message.text
    user_id = message.from_user.id  
    user = await get_user(user_id)
    lang = user['lang']

    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE company SET company_name = $1 WHERE id = $2", company_name, user['company_id'])

    await state.clear()
    if lang == 'en':
        await message.answer("Company name successfully saved.")
    elif lang == 'ru':
        await message.answer("Название компании успешно сохранено.")
    elif lang == 'uz':
        await message.answer("Kompaniya nomi muvaffaqiyatli saqlandi.")
    await navigate_to_main_menu(user_id, message.chat.id, state)