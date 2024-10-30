from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PAGE_SIZE
from database.db_utils import get_user, get_db_pool
from btns import back_page, next_page

async def show_project_workers(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    print(callback.data)
    
    project_id = int(callback.data.split("_")[-1]) if len(callback.data.split("_")) > 3 and len(callback.data.split("_")) < 5 else int(callback.data.split("_")[-2])
    page = int(callback.data.split("_")[-1]) if len(callback.data.split("_")) > 4 else 1
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    async with db_pool.acquire() as connection:
        workers = await connection.fetch("SELECT DISTINCT u.id, u.fullname FROM task t JOIN users u ON t.task_assignee_id = u.id WHERE t.project_id = $1", project_id)

    keyboard = []

    total_workers = len(workers)
    total_pages = (total_workers + PAGE_SIZE - 1) // PAGE_SIZE

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    current_workers = workers[start:end]

    text = {
        'en': f"Workers for project:\n\n",
        'ru': f"Работники проекта:\n\n",
        'uz': f"Loyiha ishchilari:\n\n"
    }

    if len(workers) == 0:
        text[lang] += "No workers found."

    for worker in current_workers:
        keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']}", callback_data=f"show_worker_{worker['id']}")])

    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"show_project_workers_{project_id}_{page - 1}")])
    if page < total_pages:   
        keyboard.append([InlineKeyboardButton(text=next_page[lang], callback_data=f"show_project_workers_{project_id}_{page + 1}")])

    keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"project_info_{project_id}")])

    await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)