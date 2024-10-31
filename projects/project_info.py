from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company

async def show_project_info(callback: types.CallbackQuery, state: FSMContext):
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
        project = await connection.fetchrow("SELECT * FROM project WHERE id = $1", project_id)
    
    text = {
        'en': f"Project info:\n\nProject name: {project['project_name']}",
        'ru': f"Информация о проекте:\n\nНазвание проекта: {project['project_name']}",
        'uz': f"Loyiha ma'lumoti:\n\nLoyiha nomi: {project['project_name']}"
    }

    keyboard = []

    if lang == 'en':
        keyboard.append([InlineKeyboardButton(text="Create task", callback_data=f"create_project_task_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Project tasks", callback_data=f"show_project_tasks_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Project workers", callback_data=f"show_project_workers_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="🔙Back", callback_data=f"show_company_projects_{user['company_id']}")])
    elif lang == 'ru':
        keyboard.append([InlineKeyboardButton(text="Создать задачу", callback_data=f"create_project_task_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Задачи проекта", callback_data=f"show_project_tasks_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Работники проекта", callback_data=f"show_project_workers_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="🔙Назад", callback_data=f"show_company_projects_{user['company_id']}")])
    elif lang == 'uz':
        keyboard.append([InlineKeyboardButton(text="Vazifa yaratish", callback_data=f"create_project_task_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Loyiha vazifalari", callback_data=f"show_project_tasks_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="Loyiha ishchilari", callback_data=f"show_project_workers_{project_id}")])
        keyboard.append([InlineKeyboardButton(text="🔙Orqaga", callback_data=f"show_company_projects_{user['company_id']}")])

    
    await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)