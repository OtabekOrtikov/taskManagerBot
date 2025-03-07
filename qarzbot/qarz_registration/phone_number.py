from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_db_pool, get_user_lang
from qarz_states import RegistrationStates
from aiogram.types import ReplyKeyboardRemove
from aiogram import types
import re

async def process_phone_number(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    phone_number = message.contact.phone_number if message.contact else message.text
    lang = await get_user_lang(message.from_user.id)

    normalized_phone_number = phone_number.lstrip('+')

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        if phone_number.startswith('+'):
            phone_number = phone_number
        else:
            phone_number = f'+{phone_number}'
        async with db_pool.acquire() as connection:
            await connection.execute("UPDATE users SET phone_number = $1 WHERE user_id = $2", phone_number, message.from_user.id)

        await state.set_state(RegistrationStates.birthdate)
        text = {
            "ru": "☑️Телефон успешно сохранен. 🗓️Теперь введите вашу дату рождения в формате ДД.ММ.ГГГГ",
            "uz": "☑️Telefon muvaffaqiyatli saqlandi. 🗓️Endi tug'ilgan kuningizni KK.OO.YYYY formatda kiriting",
            "oz": "☑️Телефон муваффақиятли сақланди. 🗓️Энди туғилган кунингизни КК.ОО.ЙЙЙЙ форматда киритинг"
        }
        await message.answer(text=text[lang], reply_markup=ReplyKeyboardRemove())
    else:
        text = {
            "ru": "❗Номер телефона введен неверно. Пожалуйста, введите номер в формате +998XXXXXXXXX",
            "uz": "❗Telefon raqami noto'g'ri kiritildi. Iltimos, telefon raqamini +998XXXXXXXXX formatda kiriting",
            "oz": "❗Телефон рақами нотўғри киритилди. Илтимос, телефон рақамини +998XXXXXXXXX форматда киритинг"
        }
        await message.answer(text=text[lang])