from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user
from qarz_utils.basic_texts import noactive_btn, back_text
from qarz_utils.btns import language_btn

async def change_lang(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    text = {
        "ru": "💬 Выберите язык",
        "uz": "💬 Tilni tanlang",
        "oz": "💬 Тилни танланг"
    }

    keyboard = language_btn[lang]

    send_message = await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})