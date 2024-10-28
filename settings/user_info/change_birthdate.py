import re
from aiogram.fsm.context import FSMContext
from btns import back_to_settings
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import UserChanges
from aiogram.types import InlineKeyboardMarkup
from aiogram import types

async def edit_birthdate(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    text = "Введите новую дату рождения в формате ДД.ММ.ГГГГ:" if lang == 'ru' else "Tug'ilgan kunni ДД.ММ.ГГГГ formatda kiriting:" if lang == 'uz' else "Enter your new birthdate in DD.MM.YYYY format:"

    keyboard = [
        [back_to_settings[lang]]
    ]
    send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(UserChanges.birthdate)

async def changing_birthdate(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    birthdate = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Check if the birthdate matches the expected format
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate):
        async with db_pool.acquire() as connection:
            await connection.execute("UPDATE users SET birthdate = $1 WHERE user_id = $2", birthdate, message.from_user.id)

        await state.clear()
        if lang == 'ru':
            await message.answer("Дата рождения успешно сохранена.")
        elif lang == 'uz':
            await message.answer("Tug'ilgan kun muvaffaqiyatli saqlandi.")
        await navigate_to_main_menu(message)
    else:
        if lang == 'ru':
            await message.answer("Неправильный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")
        elif lang == 'uz':
            await message.answer("Noto'g'ri sana formati. Iltimos, sana formatini ДД.ММ.ГГГГ da kiriting.")
        await state.set_state(UserChanges.birthdate)