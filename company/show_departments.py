from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, back_page, next_page

from config import PAGE_SIZE

async def show_departments(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    data = callback.data.split("_")
    page = int(data[2]) if len(data) > 2 else 1
    
    async with db_pool.acquire() as connection:
        if user['role_id'] == 1:
            departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1", user['company_id'])
        else:
            departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1 AND id = $2", user['company_id'], user['department_id'])
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
    
    total_departments = len(departments)
    total_pages = (total_departments + PAGE_SIZE - 1) // PAGE_SIZE

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    current_departments = departments[start:end]

    text = f"Список отделов вашей компаании “{company['company_name']}”" if user['lang'] == 'ru' else f"Sizning “{company['company_name']}” kompaniyangizning bo'limlar ro'yxati:"
    keyboard = []

    keyboard.append([InlineKeyboardButton(text="Создать отдел" if user['lang'] == 'ru' else "Bo'lim yaratish", callback_data="create_department")])

    for department in current_departments:
        keyboard.append([InlineKeyboardButton(text=f"{department['department_name']}", callback_data=f"show_department_{department['id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[user['lang']], callback_data=f"list_departments_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[user['lang']], callback_data=f"list_departments_{page + 1}")])

    keyboard.append([back_to_company[user['lang']]])

    try:
        await callback.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown'
        )
        await state.update_data(main_menu_message_id=callback.message.message_id)
    except Exception:
        sent_message = await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
        await state.update_data(main_menu_message_id=sent_message.message_id)
