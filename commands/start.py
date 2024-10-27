from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db_utils import get_db_pool, get_user
from menu.main_menu import navigate_to_main_menu

router = Router()

@router.message(F.text.startswith('/start'))
async def start_command(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    user_id = message.from_user.id

    # Check if user exists; if not, add them with role_id=1 (Boss)
    user = await get_user(user_id)
    args = message.text.split(" ", 1)
    company_id = None
    department_id = None

    await state.update_data(main_menu_message_id=0)

    # If there are any arguments after /start, parse them
    if len(args) > 1 and args[1]:
        try:
            # Assuming that the format is "1_group=1", split it
            params = args[1].split('_')
            company_id = params[0]
            if len(params) > 1:
                department_id = params[1].split('=')[1]  # Extract department_id from "group=1"

            print(f"Parsed company_id: {company_id}, department_id: {department_id}, user_id: {user_id}")  # Debugging info
        except Exception as e:
            print(f"Error parsing arguments: {e}")
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
    
    # Correct usage of db_pool.acquire with parentheses
    async with db_pool.acquire() as connection:
        if user is None:
            await connection.execute("INSERT INTO users (user_id, username, role_id) VALUES ($1, $2, 1) ON CONFLICT (user_id) DO NOTHING", user_id, message.from_user.username)
            send_message = await message.answer(text, reply_markup=keyboard)
            await state.update_data(main_menu_message_id=send_message.message_id)
        else:
            await navigate_to_main_menu(user_id, message.chat.id, state)