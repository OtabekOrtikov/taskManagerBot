from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, next_page, back_page

async def show_company_tasks(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    data = callback.data.split("_")
    page = int(data[-1]) if len(data) > 3 else 1
    
    async with db_pool.acquire() as connection:
        if user['role_id'] == 1:
            tasks = await connection.fetch("SELECT t.task_title, t.id AS task_id, u.fullname FROM task t JOIN users u ON t.task_assignee_id = u.id WHERE u.company_id = $1", user['company_id'])
        else:
            tasks = await connection.fetch("SELECT t.task_title, t.id AS task_id, u.fullname FROM task t JOIN users u ON t.task_assignee_id = u.id WHERE u.company_id = $1 AND u.department_id = $2", user['company_id'], user['department_id'])
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

    text = {
        'en': f"Tasks for {company['company_name']}:\n\n",
        'ru': f"Задачи для {company['company_name']}:\n\n",
        'uz': f"{company['company_name']} uchun vazifalar:\n\n"
    }
    keyboard_text = {
        'en': f"Create task",
        'ru': f"Создать задачу",
        'uz': f"Vazifa yaratish"
    }
    keyboard = []

    if total_tasks == 0:
        text[lang] += "No tasks found."
        keyboard.append([InlineKeyboardButton(text=keyboard_text[lang], callback_data="create_task")])

    for task in current_tasks:
        keyboard.append([InlineKeyboardButton(text=f"{task['task_title']} - {task['fullname']}", callback_data=f"task_info_{task['task_id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"show_company_tasks_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[lang], callback_data=f"show_company_tasks_{page + 1}")])

    keyboard.append([back_to_company[lang]])

    try:
        await callback.message.edit_text(
            text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown'
        )
        await state.update_data(main_menu_message_id=callback.message.message_id)
    except Exception:
        sent_message = await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
        await state.update_data(main_menu_message_id=sent_message.message_id)