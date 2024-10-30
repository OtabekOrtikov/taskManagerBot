from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_main
from states import TaskCreation
import re

async def process_assignee_phone(message: types.Message, state: FSMContext):
    assignee_phone = message.text
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    keyboard = []
        
    # Validate phone number format
    if not re.match(r'^\+998\d{9}$', assignee_phone):
        error_messages = {
            'en': "Invalid phone number format. Please enter the phone number in the format \"+998aabbbccdd\".",
            'ru': "Неверный формат номера телефона. Пожалуйста, введите номер телефона в формате \"+998aabbbccdd\".",
            'uz': "Noto'g'ri telefon raqam formati. Iltimos, telefon raqamini \"+998aabbbccdd\" formatda kiriting."
        }
        await message.answer(error_messages[lang])
        return
    
    db = get_db_pool()

    # Fetch the worker from the database
    async with db.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE phone_number = $1 AND role_id != 1", assignee_phone)

    # Handle case where no worker is found
    if not worker:
        no_worker_text = {
            'en': "No worker found with this phone number. Please enter the correct phone number.",
            'ru': "Сотрудник с таким номером телефона не найден. Пожалуйста, введите правильный номер телефона.",
            'uz': "Bu telefon raqamiga ega bo'lgan xodim topilmadi. Iltimos, to'g'ri telefon raqamini kiriting."
        }
        await message.answer(no_worker_text[lang])
        return

    # Add the worker to the keyboard with correct InlineKeyboardButton initialization
    keyboard.append([InlineKeyboardButton(text=worker['fullname'], callback_data=f"task_worker_{worker['id']}")])
    keyboard.append([back_to_main[lang]])

    # Prepare selection message based on language
    select_text = {
        'en': "Select the worker from the list:\n\nIf you want to select another worker, please enter the phone number again.",
        'ru': "Выберите сотрудника из списка:\n\nЕсли вы хотите выбрать другого сотрудника, введите номер телефона еще раз.",
        'uz': "Ro'yxatdan xodimni tanlang:\n\nAgar boshqa xodimni tanlashni istasangiz, iltimos, telefon raqamini qayta kiriting."
    }
    
    await message.answer(select_text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(task_assignee_id=worker['id'])
    await state.update_data(main_menu_message_id=message.message_id+1)
    await state.set_state(TaskCreation.task_assignee_phone)
