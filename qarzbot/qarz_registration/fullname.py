from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_db_pool, get_user_lang
from qarz_states import RegistrationStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

async def process_fullname(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    fullname = message.text

    if len(fullname) > 100:
        await message.answer("Поле ФИО не должно превышать 100 символов")
        return
    
    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)
    
    if has_numbers(fullname):
        await message.answer("Поле ФИО не должно содержать цифры")
        return

    # Correct usage of db_pool.acquire
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET fullname = $1 WHERE user_id = $2", fullname, message.from_user.id)
    
    await state.set_state(RegistrationStates.phone_number)
    lang = await get_user_lang(message.from_user.id)

    text = {
        "ru": "Введите правильный номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже",
        "uz": "To'g'ri telefon raqamni +998XXXXXXXXX formatda kiriting yoki pastdagi tugmani bosing",
        "oz": "Тўғри телефон рақамни +998XXXXXXXXX форматда киритинг ёки пастдаги тугмани босинг"
    }

    keyboard_text = {
        "ru": "Отправить номер телефона",
        "uz": "Telefon raqamni yuborish",
        "oz": "Телефон рақамни юбориш"
    }

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=keyboard_text[lang], request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)

    await message.answer(text=text[lang], reply_markup=keyboard)
    await state.set_state(RegistrationStates.phone_number)