import datetime
from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import CompanyCreation
from aiogram import types

async def process_birthdate(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    birthdate = message.text
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = await get_user_lang(message.from_user.id)

    print(f"Received birthdate: {birthdate} from user_id: {user_id}")

    try:
        date_obj = datetime.datetime.strptime(birthdate, "%d.%m.%Y")

        if date_obj.year < 1920 or date_obj.year > 2020:
            if lang == 'ru':
                raise ValueError("Год должен быть между 1920 и 2020")
            elif lang == 'uz':
                raise ValueError("Yil 1920 va 2020 oralig'ida bo'lishi kerak")
            return

        if date_obj > datetime.datetime.now():
            if lang == 'ru':
                raise ValueError("Дата рождения не может быть в будущем")
            elif lang == 'uz':
                raise ValueError("Tug'ilgan kun kelgusida bo'lishi mumkin emas")
            return

        # If the birthdate is valid, update it in the database
        async with db_pool.acquire() as connection:
            await connection.execute("""
                UPDATE users SET birthdate = $1 WHERE user_id = $2
            """, date_obj.date(), message.from_user.id)
            user_role = await connection.fetchval("SELECT role_id FROM users WHERE user_id = $1", user_id)

        # Proceed to the next state
        if user_role == 1 and user['company_id'] is None:
            await state.set_state(CompanyCreation.company_name)
            if lang == 'ru':
                await message.answer("Теперь введите название вашей компании")
            elif lang == 'uz':
                await message.answer("Endi kompaniya nomini kiriting")
        else:
            await state.clear()
            if lang == 'ru':
                await message.answer("Вы успешно завершили регистрацию")
            elif lang == 'uz':
                await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz")
            await navigate_to_main_menu(user_id, message.chat.id, state)
    except ValueError:
        if lang == 'ru':
            await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")
        elif lang == 'uz':
            await message.answer("Noto'g'ri sana formati. Iltimos, sanani KK.OO.YYYY formatda kiriting")