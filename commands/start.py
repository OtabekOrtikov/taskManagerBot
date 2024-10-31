from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_db_pool, get_user, add_user_with_role, get_department_manager
from menu.main_menu import navigate_to_main_menu

async def start_command(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    user_id = message.from_user.id

    await state.clear()

    # Check if user exists
    user = await get_user(user_id)
    args = message.text.split(" ", 1)
    company_id = None
    department_id = None

    await state.update_data(main_menu_message_id=0)

    # Parse referral link parameters if they exist
    if len(args) > 1 and args[1]:
        try:
            # Split the parameters and validate the format
            params = args[1].split('_')
            if len(params) == 2 and params[1].startswith("department="):
                company_id = int(params[0])
                department_id = int(params[1].split('=')[1])
            else:
                raise ValueError("Invalid referral format.")
        except Exception as e:
            await message.reply("Ошибка в параметрах ссылки. Пожалуйста, проверьте правильность ссылки.")
            return

    text = """Привет! Я помогу тебе управлять проектами. Для начала, выберите язык.
    
---------------------------------------------------------------------

Salom! Men sizga loyihalarni boshqarishda yordam beraman. Boshlash uchun tilni tanlang."""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")
        ]
    ])
    
    async with db_pool.acquire() as connection:
        if user is None:
            # Determine the role based on referral link information
            if company_id and department_id:
                # Check if there is already a Manager for this department
                manager_exists = await get_department_manager(connection, company_id, department_id)
                
                # Assign Manager if no manager exists, else assign Worker
                role_id = 2 if not manager_exists else 3
            else:
                # Assign Boss role if no referral link is used
                role_id = 1

            # Add the user to the database with the determined role
            await add_user_with_role(connection, user_id, message.from_user.username, role_id, company_id, department_id)
            
            # Send welcome message
            send_message = await message.answer(text, reply_markup=keyboard)
            await state.update_data(main_menu_message_id=send_message.message_id)
        else:
            # Navigate to the main menu if user already exists
            await navigate_to_main_menu(user_id, message.chat.id, state)
