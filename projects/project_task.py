from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_page

async def show_project_tasks(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    project_id = int(callback.data.split("_")[-1])
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    async with db_pool.acquire() as connection:
        tasks = await connection.fetch("""SELECT t.id as task_id, t.task_title, u.fullname
                                          FROM task t
                                          JOIN users u ON t.task_assignee_id = u.id
                                          WHERE t.project_id = $1""", 
                                      project_id)
    
    text = {
        'en': f"Tasks for project:\n\n",
        'ru': f"Задачи проекта:\n\n",
        'uz': f"Loyiha vazifalari:\n\n"
    }

    keyboard = []


    if len(tasks) == 0:
        text[lang] += "No tasks found."

    for task in tasks:
        keyboard.append([InlineKeyboardButton(text=f"{task['task_title']} - {task['fullname']}", callback_data=f"task_info_{task['task_id']}")])
    
    keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"project_info_{project_id}")])   
    await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)