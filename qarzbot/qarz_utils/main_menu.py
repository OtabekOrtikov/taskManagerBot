from aiogram.fsm.context import FSMContext
from qarz_config import API_TOKEN
from qarz_database.db_utils import get_user
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from qarz_utils.missed_fields import missed_field
from qarz_utils.btns import main_menu_btn

bot = Bot(token=API_TOKEN)

async def main_menu(user_id: int, chat_id: int, state: FSMContext):
    data = await state.get_data()
    main_menu_message_id = data.get("main_message_id")
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        "ru": "🏠Главное меню",
        "uz": "🏠Asosiy menyu",
        "oz": "🏠Асосий меню"
    }

    if main_menu_message_id:
        try:
            await bot.edit_message_text(
                text[lang], chat_id=chat_id,
                message_id=main_menu_message_id
            )
        except Exception:
            sent_message = await bot.send_message(chat_id, text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=main_menu_btn[lang]))
            await state.update_data(main_message_id=sent_message.message_id)
    else:
        sent_message = await bot.send_message(chat_id, text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=main_menu_btn[lang]))
        await state.update_data(main_message_id=sent_message.message_id)