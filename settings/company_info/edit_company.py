from aiogram.fsm.context import FSMContext
from btns import company_info_btns
from database.db_utils import get_db_pool, get_user, get_user_lang
from menu.main_menu import navigate_to_main_menu
from states import CompanyChanges
from aiogram.types import InlineKeyboardMarkup
from aiogram import types

async def edit_company_info(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    
    async with db_pool.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        workers_count = await connection.fetchval("SELECT COUNT(*) FROM users WHERE company_id = $1", user['company_id'])
        departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1", user['company_id'])
        departments_count = len(departments)

    if lang == 'en':
        text = (
            f"Company information:\n\n"
            f"Company name: {company['company_name']}\n"
            f"Number of departments: {departments_count}\n\n"
            f"Number of workers: {workers_count}\n"
            f"Choose the information you want to change:"
        )
    elif lang == 'ru':
        text = (
            f"Информация о компании:\n\n"
            f"Название компании: {company['company_name']}\n"
            f"Количество отделов: {departments_count}\n\n"
            f"Количество работников: {workers_count}\n"
            f"Выберите информацию, которую хотите изменить:"
        )
    elif lang == 'uz':
        text = (
            f"Kompaniya haqida ma'lumot:\n\n"
            f"Kompaniya nomi: {company['company_name']}\n"
            f"Bo'limlar soni: {departments_count}\n\n"
            f"Ishchilar soni: {workers_count}\n"
            f"O'zgartirmoqchi bo'lgan ma'lumotni tanlang:"
        )

    send_message = await callback.message.edit_text(text, reply_markup=company_info_btns[lang])
    await state.update_data(main_menu_message_id=send_message.message_id)