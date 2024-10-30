from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool

async def show_worker(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    # Extract worker ID from callback data
    worker_id = int(callback.data.split("_")[-1])

    async with db_pool.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        department = await connection.fetchrow("SELECT * FROM department WHERE id = $1", worker['department_id'])

    if worker['role_id'] == 1:
        if lang == 'ru':
            worker_role = "Руководитель"
        elif lang == 'uz':
            worker_role = "Boshqaruvchi"
        elif lang == 'en':
            worker_role = "Boss"
    elif worker['role_id'] == 2:
        if lang == 'ru':
            worker_role = "Руководитель отдела"
        elif lang == 'uz':
            worker_role = "Bo‘lim boshqaruvchisi"
        elif lang == 'en':
            worker_role = "Department head"
    else:
        if lang == 'ru':
            worker_role = "Сотрудник"
        elif lang == 'uz':
            worker_role = "Xodim"
        elif lang == 'en':
            worker_role = "Employee"

    if lang == 'en':
        text = f"Worker details:\n"
        text += f"Full name: {worker['fullname']}\n"
        text += f"Username: {f"@{worker['username']}" if worker['username'] else ""}\n" 
        text += f"Phone: {worker['phone_number']}\n"
        text += f"Birthdate: {worker['birthdate']}\n"
        text += f"Position: {worker_role}\n"
        text += f"Department: {department['department_name']}\n\n"
        if user['role_id'] == 1:
            text += f"Do you want to change the user role? Use the buttons below."
    elif lang == 'ru':
        text = f"Информация о сотруднике:\n"
        text += f"ФИО: {worker['fullname']}\n"
        text += f"Имя пользователя: {f'@{worker['username']}' if worker['username'] else ''}\n"
        text += f"Телефон: {worker['phone_number']}\n"
        text += f"Дата рождения: {worker['birthdate']}\n"
        text += f"Должность: {worker_role}\n"
        text += f"Отдел: {department['department_name']}\n\n"
        if user['role_id'] == 1:
            text += f"Хотите изменить роль пользователя? Используйте кнопки ниже."
    elif lang == 'uz':
        text = f"Xodim ma'lumotlari:\n"
        text += f"FIO: {worker['fullname']}\n"
        text += f"Foydalanuvchi nomi: {f'@{worker['username']}' if worker['username'] else ''}\n"
        text += f"Telefon raqami: {worker['phone_number']}\n"
        text += f"Tug'ilgan kun: {worker['birthdate']}\n"
        text += f"Lavozimi: {worker_role}\n"
        text += f"Bo'lim: {department['department_name']}\n\n"
        if user['role_id'] == 1:
            text += f"Foydalanuvchi lavozimini o'zgartirmoqchimisiz? Quyidagi tugmalar orqali ishlatishingiz mumkin."

    # Build message text and keyboard
    keyboard = []

    if lang == 'en':
        keyboard.append([InlineKeyboardButton(text="List worker tasks", callback_data=f"list_tasks_{worker_id}")])
        if user['role_id'] == 1:
            keyboard.append([InlineKeyboardButton(text="Change user role", callback_data=f"change_user_role_{worker_id}")])
    elif lang == 'ru':
        keyboard.append([InlineKeyboardButton(text="Список задач сотрудника", callback_data=f"list_tasks_{worker_id}")])
        if user['role_id'] == 1:
            keyboard.append([InlineKeyboardButton(text="Изменить роль пользователя", callback_data=f"change_user_role_{worker_id}")])
    elif lang == 'uz':
        keyboard.append([InlineKeyboardButton(text="Xodim vazifalari ro‘yxati", callback_data=f"list_tasks_{worker_id}")])
        if user['role_id'] == 1:
            keyboard.append([InlineKeyboardButton(text="Foydalanuvchi lavozimini o'zgartirish", callback_data=f"change_user_role_{worker_id}")])

    # Add a back button
    keyboard.append([InlineKeyboardButton(text="🔙 Назад" if lang == 'ru' else "🔙 Orqaga", callback_data="list_workers")])

    # Send the message
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)