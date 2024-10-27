from aiogram.fsm.context import FSMContext
from db_utils import get_db_pool, get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def process_department_name(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    department_name = message.text
    lang = await get_user_lang(message.from_user.id)

    async with db_pool.acquire() as connection:
        company_id = await connection.fetchval("SELECT company_id FROM users WHERE user_id = $1", message.from_user.id)
        await connection.execute("INSERT INTO department (department_name, company_id) VALUES ($1, $2)", department_name, company_id)
        department_id = await connection.fetchval("SELECT id FROM department WHERE department_name = $1", department_name)
        department_name = await connection.fetchval("SELECT department_name FROM department WHERE id = $1", department_id)

    # Prepare referral link for the newly created department
    if lang == 'ru':
        department_msg = (
            f"Отдел '{department_name}' успешно создан! Вы можете продолжить добавлять отделы или нажать 'Завершить' для выхода."
        )
        continue_text = "Продолжить"
        finish_text = "Завершить"
    else:
        department_msg = (
            f"'{department_name}' bo‘limi muvaffaqiyatli yaratildi! Bo‘lim qo‘shishni davom ettiring yoki chiqish uchun 'Tugatish' tugmasini bosing."
        )
        continue_text = "Davom etish"
        finish_text = "Tugatish"

    # Options for the user to continue adding departments or finish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=continue_text, callback_data="continue_department_creation")],
        [InlineKeyboardButton(text=finish_text, callback_data="finish_department_creation")]
    ])

    send_message = await message.answer(department_msg, reply_markup=keyboard)
    await state.update_data(main_menu_message_id= send_message.message_id + 1)