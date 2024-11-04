from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang, get_db_pool
from btns import back_to_main
from states import TaskCreation

from utils.escape_markdown import escape_markdown_v2

async def create_project_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    data = callback.data.split("_")
    project_id = int(data[-1])

    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    db = get_db_pool()

    async with db.acquire() as connection:
        project = await connection.fetchrow("SELECT * FROM project WHERE id = $1", project_id)

    # Escape project name to prevent Markdown parsing errors
    project_name = escape_markdown_v2(project['project_name'])

    if lang == 'en':
        text = f"Great, you are creating a task for project **{project_name}**\n\nPlease enter the task name. Maximum 30 characters."
    elif lang == 'ru':
        text = f"Отлично, вы создаете задачу для проекта **{project_name}**\n\nВведите название задачи. Максимум 30 символов."
    elif lang == 'uz':
        text = f"Ajoyib, siz **{project_name}** loyihasi uchun vazifa yaratmoqdasiz\n\nVazifa nomini kiriting. Maksimum 30 belgi."

    send_message = await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]]))
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.update_data(project_id=project_id)
    await state.set_state(TaskCreation.task_title)
