from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_utils import get_user, get_db_pool
from btns import settings_menu_btns, back_to_main

async def show_settings(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    role = user['role_id']
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")
    
    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    await state.clear()
    
    async with db_pool.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        workers_count = await connection.fetchval("SELECT COUNT(*) FROM users WHERE company_id = $1", user['company_id'])
        department_count = await connection.fetchval("SELECT COUNT(*) FROM department WHERE company_id = $1", user['company_id'])
    
    # Determine the username text
    username_text = f"@{user['username']}" if user['username'] else "Не указан" if lang == 'ru' else "Belgilanmagan"
    role_text = "Руководитель компании" if role == 1 else "Руководитель отдела" if role == 2 else "Сотрудник"

    if lang == 'ru':
        text = (
            f"**Информация о вас:**\n"
            f"Имя: **{user['fullname']}**\n"
            f"Логин: **{username_text}**\n"
            f"Номер телефона: **{user['phone_number']}**\n"
            f"Должность: **{role_text}**\n"
            f"Дата рождения: **{user['birthdate']}**\n"
            f"Дата регистрации: **{user['registration_date']}**\n"
            f"Язык интерфейса: **Русский**\n"
            f"Компания: **{company['company_name']}**\n\n"
        )
    elif lang == 'uz':
        text = (
            f"**Siz haqingizdagi ma'lumotlar:**\n"
            f"F.I.O.: **{user['fullname']}**\n"
            f"Login: **{username_text}**\n"
            f"Telefon raqami: **{user['phone_number']}**\n"
            f"Lavozim: **{role_text}**\n"
            f"Tug'ilgan kun: **{user['birthdate']}**\n"
            f"Ro'yxatdan o'tgan sana: **{user['registration_date']}**\n"
            f"Interfeyz til: **O'zbek**\n"
            f"Kompaniya: **{company['company_name']}**\n"
        )

    # Initialize keyboard and define the message content based on role and language
    keyboard = []
    if role == 1:  # Admin
        if lang == 'ru':
            text += (
                f"Количество сотрудников: {workers_count}\n"
                f"Количество отделов: {department_count}\n\n"
                f"Если хотите изменить какую-ту информацию, нажмите на кнопку ниже."
            )
        elif lang == 'uz':
            text += (
                f"Xodimlar soni: {workers_count}\n"
                f"Bo'limlar soni: {department_count}\n\n"
                f"Agar biror ma'lumotni o'zgartirishni xohlaysiz, quyidagi tugmani bosing."
            )
    else:  # Regular User
        if lang == 'ru':
            text += (
                f"Если хотите изменить информацию о себе, нажмите на кнопку ниже."
            )
        elif lang == 'uz':
            text += (
                f"Agar o'zingiz haqingizdagi ma'lumotni o'zgartirishni xohlaysiz, quyidagi tugmani bosing."
            )

    # Add main settings menu and back button
    keyboard.append([settings_menu_btns[lang]])  # Main settings button
    if role == 1:
        keyboard.append([InlineKeyboardButton(text="Изменить компанию", callback_data="change_company")])
    keyboard.append([back_to_main[lang]])  # Back button

    # Build InlineKeyboardMarkup with the corrected keyboard
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    # Send or edit the message
    send_message = await callback.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await state.update_data(main_menu_message_id=send_message.message_id)