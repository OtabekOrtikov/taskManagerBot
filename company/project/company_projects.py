from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, next_page, back_page

async def show_company_projects(callback: types.CallbackQuery, state: FSMContext):
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
        projects = await connection.fetch("SELECT * FROM project WHERE boss_id = $1", user['id'])
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
    
    total_projects = len(projects)
    total_pages = (total_projects + 5 - 1) // 5

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * 5
    end = start + 5
    current_projects = projects[start:end]

    text = {
        'en': f"Projects for {company['company_name']}:\n\n",
        'ru': f"Проекты для {company['company_name']}:\n\n",
        'uz': f"{company['company_name']} uchun loyihalar:\n\n"
    }
    keyboard_text = {
        'en': f"Create project",
        'ru': f"Создать проект",
        'uz': f"Loyiha yaratish"
    }
    keyboard = []

    if total_projects == 0:
        text[lang] += "No projects found."
        keyboard.append([InlineKeyboardButton(text=keyboard_text[lang], callback_data="create_project")])

    for project in current_projects:
        keyboard.append([InlineKeyboardButton(text=f"{project['project_name']}", callback_data=f"project_info_{project['id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"show_company_projects_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[lang], callback_data=f"show_company_projects_{page + 1}")])

    keyboard.append([back_to_company[lang]])

    try:
        await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    except Exception as e:
        print(e)
        await callback.answer("An error occurred. Please try again later.")
        return
    
    await state.update_data(main_menu_message_id=callback.message.message_id)