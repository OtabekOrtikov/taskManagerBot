from aiogram.fsm.context import FSMContext
from db_utils import get_db_pool, get_user_lang
from states import RegistrationStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

async def process_fullname(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    fullname = message.text

    # Correct usage of db_pool.acquire
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET fullname = $1 WHERE user_id = $2", fullname, message.from_user.id)
    
    await state.set_state(RegistrationStates.phone_number)
    lang = await get_user_lang(message.from_user.id)
    if lang == 'ru':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже", reply_markup=keyboard)
    elif lang == 'uz':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("To'g'ri telefon raqamni +998XXXXXXXXX formatda kiriting yoki pastdagi tugmani bosing", reply_markup=keyboard)