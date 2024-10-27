from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user_lang
from states import DepartmentCreation
from aiogram import types

async def process_company_name(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    company_name = message.text
    lang = await get_user_lang(message.from_user.id)

    async with db_pool.acquire() as connection:
        await connection.execute("INSERT INTO company (company_name) VALUES ($1)", company_name)
        company_id = await connection.fetchval("SELECT id FROM company WHERE company_name = $1", company_name)
        await connection.execute("UPDATE users SET company_id = $1 WHERE user_id = $2", company_id, message.from_user.id)

    await state.set_state(DepartmentCreation.department_name)
    if lang == 'ru':
        await message.answer("Вы успешно завершили регистрацию. Теперь, давайте добавим название отдела или рабочий группы.")
    elif lang == 'uz':
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Endi, bo'lim yoki ish guruhi nomini qo'shaylik.")
