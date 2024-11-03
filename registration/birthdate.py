import datetime
from aiogram.fsm.context import FSMContext
from config import API_TOKEN
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import CompanyCreation
from aiogram import types, Bot

bot = Bot(token=API_TOKEN)

async def process_birthdate(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    birthdate = message.text
    user_id = message.from_user.id
    user = await get_user(user_id)
    user_role = user['role_id']
    lang = await get_user_lang(message.from_user.id)

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
            boss_id = await connection.fetchval("SELECT user_id FROM users WHERE company_id = $1 AND role_id = 1", user['company_id'])
            if user['department_id']:
                department = await connection.fetchrow("SELECT department_name FROM departments WHERE id = $1", user['department_id'])
                manager_id = await connection.fetchval("SELECT user_id FROM users WHERE company_id = $1 AND department_id = $2 AND role_id = 2", user['company_id'], user['department_id'])

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
                await bot.send_message(boss_id, f"Пользователь {user['fullname']} успешно зарегистрировался на отдел {department['department_name']}") 
                if manager_id:
                    await bot.send_message(manager_id, f"Пользователь {user['fullname']} успешно зарегистрировался на отдел {department['department_name']}")
            elif lang == 'uz':
                await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz")
                await bot.send_message(boss_id, f"Foydalanuvchi {user['fullname']} muvaffaqiyatli ro'yxatdan o'tdi {department['department_name']} bo'limi")
                if manager_id:
                    await bot.send_message(manager_id, f"Foydalanuvchi {user['fullname']} muvaffaqiyatli ro'yxatdan o'tdi {department['department_name']} bo'limi")
            await navigate_to_main_menu(user_id, message.chat.id, state)
    except ValueError:
        if lang == 'ru':
            await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")
        elif lang == 'uz':
            await message.answer("Noto'g'ri sana formati. Iltimos, sanani KK.OO.YYYY formatda kiriting")