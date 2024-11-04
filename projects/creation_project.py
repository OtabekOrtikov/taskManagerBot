from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.db_utils import get_user, get_db_pool
from btns import settings_menu_btns, back_to_main
from menu.main_menu import navigate_to_main_menu
from states import ProjectCreation

async def create_project(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    if lang == "ru":
        send_message = await callback.message.edit_text("Вы создаете проект.\nВведите название проекта.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]]))
    elif lang == "uz":
        send_message = await callback.message.edit_text("Siz loyihani yaratyapsiz.\nLoyiha nomini kiriting.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]]))

    await state.set_state(ProjectCreation.project_name)
    await state.update_data(main_menu_message_id=send_message.message_id)

async def creating_project(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    db_pool = get_db_pool()

    async with db_pool.acquire() as connection:
        await connection.execute("INSERT INTO project (project_name, boss_id) VALUES ($1, $2)", message.text, user['id'])

    # Response messages
    if lang == "en":
        await message.answer(f"Project **{message.text}** has been successfully created. If you want to add participants, create a task for this project.", parse_mode="Markdown")
    elif lang == "ru":
        await message.answer(f"Проект **{message.text}** успешно создан. Если хотите добавить участников, создайте для этого проекта задачу.", parse_mode="Markdown")
    elif lang == "uz":
        await message.answer(f"**{message.text}** loyihasi muvaffaqiyatli yaratildi. Agar qatnashchilarni qo'shmoqchi bo'lsangiz, ushbu loyiha uchun vazifa yarating.", parse_mode="Markdown")

    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)
