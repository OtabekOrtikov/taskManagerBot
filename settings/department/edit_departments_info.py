from aiogram.fsm.context import FSMContext
from btns import back_to_edit_company, back_page, next_page
from config import PAGE_SIZE
from database.db_utils import get_db_pool, get_user
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

async def edit_departments(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    db_pool = get_db_pool()
    async with db_pool.acquire() as connection:
        departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1 ORDER BY status != 'active'", user['company_id'])
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])


    if lang == 'en':
        text = (
            f"Departments of **{company['company_name']}**:\n\n"
            f"Number of departments: {len(departments)}\n\n"
            f"Choose the department you want to edit:"
        )
    elif lang == 'ru':
        text = (
            f"Отделы **{company['company_name']}**:\n\n"
            f"Количество отделов: {len(departments)}\n\n"
            f"Выберите отдел, который хотите изменить:"
        )
    elif lang == 'uz':
        text = (
            f"**{company['company_name']}** bo'limlari:\n\n"
            f"Bo'limlar soni: {len(departments)}\n\n"
            f"O'zgartirmoqchi bo'lgan bo'limni tanlang:"
        )
    
    data = callback.data.split("_")
    page = int(data[-1]) if len(data) > 2 else 1

    total_departments = len(departments)
    total_pages = (total_departments + PAGE_SIZE - 1) // PAGE_SIZE

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    current_departments = departments[start:end]

    keyboard = []

    for department in current_departments:
        if department['status'] == 'active':
            keyboard_text = f"{department['department_name']}"
        else:
            if lang == 'en':
                keyboard_text = f"{department['department_name']} - Not active"
            elif lang == 'ru':
                keyboard_text = f"{department['department_name']} - Не актив"
            elif lang == 'uz':
                keyboard_text = f"{department['department_name']} - Aktiv emas"
        keyboard.append([InlineKeyboardButton(text=keyboard_text, callback_data=f"edit_department_{department['id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[user['lang']], callback_data=f"edit_departments_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[user['lang']], callback_data=f"edit_departments_{page + 1}")])

    keyboard.append([back_to_edit_company[user['lang']]])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )
    await state.update_data(main_menu_message_id=callback.message.message_id)
    