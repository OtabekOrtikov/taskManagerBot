from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_utils import get_user, get_db_pool
from btns import back_to_company, next_page, back_page

async def show_company_tasks(callback: types.CallbackQuery, state: FSMContext):
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
        tasks = await connection.fetch("SELECT * FROM task WHERE company_id = $1", user['company_id'])
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
    
    total_tasks = len(tasks)
    total_pages = (total_tasks + 5 - 1) // 5

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * 5
    end = start + 5
    current_tasks = tasks[start:end]

    text = f"Список задач вашей компании “{company['company_name']}”" if user['lang'] == 'ru' else f"Sizning “{company['company_name']}” kompaniyangizning vazifalar ro'yxati:"
    keyboard = []

    for task in current_tasks:
        keyboard.append([InlineKeyboardButton(text=f"{task['task_name']}", callback_data=f"show_task_{task['id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[user['lang']], callback_data=f"list_tasks_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[user['lang']], callback_data=f"list_tasks_{page + 1}")])

    keyboard.append([back_to_company[user['lang']]])

    try:
        await callback.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown'
        )
        await state.update_data(main_menu_message_id=callback.message.message_id)
    except Exception:
        sent_message = await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
        await state.update_data(main_menu_message_id=sent_message.message_id)