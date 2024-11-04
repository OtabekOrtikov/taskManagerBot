from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool

async def show_worker(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    # Extract worker ID from callback data
    worker_id = int(callback.data.split("_")[-1])

    async with db_pool.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        if worker:
            department = await connection.fetchrow("SELECT * FROM department WHERE id = $1", worker['department_id']) if worker['department_id'] else None

    # Define roles based on language and role_id
    roles = {
        1: {"ru": "Руководитель", "uz": "Boshqaruvchi", "en": "Boss"},
        2: {"ru": "Руководитель отдела", "uz": "Bo‘lim boshqaruvchisi", "en": "Department head"},
        3: {"ru": "Сотрудник", "uz": "Xodim", "en": "Employee"}
    }
    worker_role = roles.get(worker['role_id'], {}).get(lang, "Employee")

    # Generate text based on language
    text_template = {
        'en': (
            "Worker details:\n"
            f"Full name: {worker['fullname']}\n"
            f"Username: {'@' + worker['username'] if worker['username'] else ''}\n"
            f"Phone: {worker['phone_number']}\n"
            f"Birthdate: {worker['birthdate']}\n"
            f"Position: {worker_role}\n"
            f"Department: {department['department_name'] if department else 'N/A'}\n\n"
            + (f"Do you want to change the user role? Use the buttons below." if user['role_id'] == 1 else "")
        ),
        'ru': (
            "Информация о сотруднике:\n"
            f"ФИО: {worker['fullname']}\n"
            f"Имя пользователя: {'@' + worker['username'] if worker['username'] else ''}\n"
            f"Телефон: {worker['phone_number']}\n"
            f"Дата рождения: {worker['birthdate']}\n"
            f"Должность: {worker_role}\n"
            f"Отдел: {department['department_name'] if department else 'N/A'}\n\n"
            + (f"Хотите изменить роль пользователя? Используйте кнопки ниже." if user['role_id'] == 1 else "")
        ),
        'uz': (
            "Xodim ma'lumotlari:\n"
            f"FIO: {worker['fullname']}\n"
            f"Foydalanuvchi nomi: {'@' + worker['username'] if worker['username'] else ''}\n"
            f"Telefon raqami: {worker['phone_number']}\n"
            f"Tug'ilgan kun: {worker['birthdate']}\n"
            f"Lavozimi: {worker_role}\n"
            f"Bo'lim: {department['department_name'] if department else 'N/A'}\n\n"
            + (f"Foydalanuvchi lavozimini o'zgartirmoqchimisiz? Quyidagi tugmalar orqali ishlatishingiz mumkin." if user['role_id'] == 1 else "")
        )
    }
    text = text_template.get(lang, text_template['en'])

    # Build the inline keyboard based on language
    keyboard = [
        [InlineKeyboardButton(
            text="List worker tasks" if lang == 'en' else "Список задач сотрудника" if lang == 'ru' else "Xodim vazifalari ro‘yxati",
            callback_data=f"list_tasks_{worker_id}"
        )]
    ]
    if user['role_id'] == 1:
        keyboard.append([
            InlineKeyboardButton(
                text="Change user role" if lang == 'en' else "Изменить роль пользователя" if lang == 'ru' else "Foydalanuvchi lavozimini o'zgartirish",
                callback_data=f"change_user_role_{worker_id}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад" if lang == 'ru' else "🔙 Orqaga" if lang == 'uz' else "🔙 Back",
            callback_data="list_workers"
        )
    ])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)
