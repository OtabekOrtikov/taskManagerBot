from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from menu.main_menu import navigate_to_main_menu

async def activate_department(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    data = callback.data.split("_")
    department_id = int(data[-1])

    if lang == 'en':
        text = "Are you sure you want to activate this department?"
        yes_text = "Yes"
        no_text = "No"
    elif lang == 'ru':
        text = "Вы уверены, что хотите активировать этот отдел?"
        yes_text = "Да"
        no_text = "Нет"
    elif lang == 'uz':
        text = "Ushbu bo'limni faollashtirishni istaysizmi?"
        yes_text = "Ha"
        no_text = "Yo'q"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data=f"confirm_activate_department_{department_id}"),
                InlineKeyboardButton(text=no_text, callback_data=f"edit_department_{department_id}")
            ]
        ]
    ))
    await state.update_data({"main_menu_message_id": callback.message.message_id})

async def confirm_activate_department(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    data = callback.data.split("_")
    department_id = int(data[-1])

    db_pool = get_db_pool()
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE department SET status = 'active' WHERE id = $1", department_id)
    
    if lang == 'en':
        text = "Department activated successfully."
    elif lang == 'ru':
        text = "Отдел успешно активирован."
    elif lang == 'uz':
        text = "Bo'lim muvaffaqiyatli faollashtirildi."

    await callback.message.edit_text(text)
    await state.clear()
    await navigate_to_main_menu(user_id, callback.message.chat.id, state)