from aiogram.fsm.context import FSMContext
from config import API_TOKEN
from database.db_utils import get_db_pool
from aiogram import Bot
from btns import main_menu_btns

bot = Bot(token=API_TOKEN)

async def navigate_to_main_menu(user_id: int, chat_id: int, state: FSMContext):
    db_pool = get_db_pool()
    """Navigates the user back to the main menu, displaying options based on role and language."""
    # Retrieve main menu message ID from state
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    # Fetch user details: role and language
    async with db_pool.acquire() as connection:
        user = await connection.fetchrow("SELECT role_id, lang FROM users WHERE user_id = $1", user_id)
    
    if user is None:
        await bot.send_message(chat_id, "User not found. Please register again with /start.")
        return

    lang = user['lang']

    text = {
        'en': "Main menu",
        'ru': "Главное меню",
        'uz': "Asosiy menyu"
    }

    # Set up menu text and dynamically create keyboard based on role and language
    keyboard = []

    if user['role_id'] == 1:
        # Admin
        keyboard = main_menu_btns['boss'][lang]
    elif user['role_id'] == 2:
        # Manager
        keyboard = main_menu_btns['manager'][lang]
    else:
        # Employee
        keyboard = main_menu_btns['worker'][lang]

    # Attempt to edit the existing main menu message or send a new one if editing fails
    if main_menu_message_id:
        try:
            await bot.edit_message_text(
                text[lang], chat_id=chat_id,
                message_id=main_menu_message_id, reply_markup=keyboard
            )
        except Exception:
            sent_message = await bot.send_message(chat_id, text[lang], reply_markup=keyboard)
            await state.update_data(main_menu_message_id=sent_message.message_id)
    else:
        sent_message = await bot.send_message(chat_id, text[lang], reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)
