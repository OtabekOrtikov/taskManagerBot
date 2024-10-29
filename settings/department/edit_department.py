from aiogram.fsm.context import FSMContext
from btns import back_to_edit_company
from database.db_utils import get_db_pool, get_user
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

async def edit_department(callback: types.CallbackQuery, state: FSMContext):
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
        worker_count = await connection.fetchval("SELECT COUNT(*) FROM users WHERE department_id = $1", department_id)
    
    if lang == 'en':
        text = (
            f"Department name: **{department['department_name']}**\n"
            f"We have **{worker_count}** workers in this department.\n\n"
            f"What do you want to do with this department?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Change department name", callback_data=f"change_department_name_{department_id}")],
            [InlineKeyboardButton(text="Delete department", callback_data=f"delete_department_{department_id}")] if department['status'] == 'active' else [InlineKeyboardButton(text="Activate department", callback_data=f"activate_department_{department_id}")],
            [InlineKeyboardButton(text="🔙Back", callback_data="edit_departments")]
        ]
    elif lang == 'ru':
        text = (
            f"Название отдела: **{department['department_name']}**\n"
            f"В этом отделе работает **{worker_count}** сотрудников.\n\n"
            f"Что вы хотите сделать с этим отделом?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Изменить название отдела", callback_data=f"change_department_name_{department_id}")],
            [InlineKeyboardButton(text="Удалить отдел", callback_data=f"delete_department_{department_id}")] if department['status'] == 'active' else [InlineKeyboardButton(text="Активировать отдел", callback_data=f"activate_department_{department_id}")],
            [InlineKeyboardButton(text="🔙Назад", callback_data="edit_departments")]
        ]
    elif lang == 'uz':
        text = (
            f"Bo'lim nomi: **{department['department_name']}**\n"
            f"Ushbu bo'limda **{worker_count}** xodim ishlaydi.\n\n"
            f"Ushbu bo'lim bilan nima qilmoqchisiz?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Bo'lim nomini o'zgartirish", callback_data=f"change_department_name_{department_id}")],
            [InlineKeyboardButton(text="Bo'limni o'chirish", callback_data=f"delete_department_{department_id}")] if department['status'] == 'active' else [InlineKeyboardButton(text="Bo'limni faollashtirish", callback_data=f"activate_department_{department_id}")],
            [InlineKeyboardButton(text="🔙Orqaga", callback_data="edit_departments")]
        ]
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="Markdown")
    await state.update_data({"main_menu_message_id": callback.message.message_id})