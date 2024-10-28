from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from menu.main_menu import navigate_to_main_menu
from states import DepartmentChanges

async def edit_department_name(callback: types.CallbackQuery, state: FSMContext):
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
        department = await connection.fetchrow("SELECT * FROM department WHERE id = $1", department_id)

    if lang == 'en':
        text = f"Enter the new name for the department **{department['department_name']}**:"
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Back", callback_data=f"edit_department_{department_id}")]
        ]
    elif lang == 'ru':
        text = f"Введите новое название для отдела **{department['department_name']}**:"
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edit_department_{department_id}")]
        ]
    elif lang == 'uz':
        text = f"**{department['department_name']}** bo'limi uchun yangi nomni kiriting:"
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"edit_department_{department_id}")]
        ]

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="Markdown")
    await state.update_data({"main_menu_message_id": callback.message.message_id})
    await state.update_data({"department_id": department_id})
    await state.set_state(DepartmentChanges.department_name)

async def changing_department_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    department_name = message.text

    db_pool = get_db_pool()

    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE department SET department_name = $1 WHERE id = $2", department_name, data['department_id'])
    
    if lang == 'en':
        text = f"The department name has been successfully changed to **{department_name}**."
    elif lang == 'ru':
        text = f"Название отдела успешно изменено на **{department_name}**."
    elif lang == 'uz':
        text = f"Bo'lim nomi muvaffaqiyatli **{department_name}** ga o'zgartirildi."

    await message.answer(text, parse_mode="Markdown")
    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)