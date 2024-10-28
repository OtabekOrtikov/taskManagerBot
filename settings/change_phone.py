from aiogram.fsm.context import FSMContext
from btns import back_to_settings
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import UserChanges
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram import types
import re

async def edit_phone(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    text = "Введите новый номер телефона:" if lang == 'ru' else "Yangi telefon raqamingizni kiriting:" if lang == 'uz' else "Enter your new phone number:"

    keyboard = [
        [back_to_settings[lang]]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    if lang == 'ru':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        send_message = await callback.message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже", reply_markup=keyboard)
    elif lang == 'uz':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        send_message = await callback.message.answer("To'g'ri telefon raqamni +998XXXXXXXXX formatda kiriting yoki pastdagi tugmani bosing", reply_markup=keyboard)
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(UserChanges.phone_number)


async def changing_phone_number(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    phone_number = message.contact.phone_number if message.contact else message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    normalized_phone_number = phone_number.lstrip('+')

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        async with db_pool.acquire() as connection:
            await connection.execute("UPDATE users SET phone_number = $1 WHERE user_id = $2", phone_number, message.from_user.id)

        await state.clear()
        if lang == 'ru':
            await message.answer("Телефон успешно сохранен.")
        elif lang == 'uz':
            await message.answer("Telefon muvaffaqiyatli saqlandi.")
        
        await state.clear()
        await navigate_to_main_menu(user_id, message.chat.id, state)
    else:
        if lang == 'ru':
            await message.answer("Номер телефона введен неверно. Пожалуйста, введите номер в формате +998XXXXXXXXX")
        elif lang == 'uz':
            await message.answer("Telefon raqami noto'g'ri kiritildi. Iltimos, telefon raqamini +998XXXXXXXXX formatda kiriting")