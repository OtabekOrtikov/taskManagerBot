from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user
from qarz_utils.basic_texts import noactive_btn, back_text

async def show_settings(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    text = {
        "ru": "⚙️ Настройки.\n\n👇 Выберите, что хотите настроить.",
        "uz": "⚙️ Sozlamalar.\n\n👇 Qaysi sozlamalarni sozlashni xohlaysiz.",
        "oz": "⚙️ Созламалар.\n\n👇 Қайси созламаларни созлашни хоҳлайсиз."
    }

    keyboard_text = {
        "user": {
            "ru": "👤 Данные пользователя",
            "uz": "👤 Foydalanuvchi ma'lumotlari",
            "oz": "👤 Фойдаланувчи маълумотлари"
        },
        "lang": {
            "ru": "🌐 Язык",
            "uz": "🌐 Til",
            "oz": "🌐 Тил"
        }
    }

    keyboard = [
        [InlineKeyboardButton(text=keyboard_text["user"][lang], callback_data="userdata")],
        [InlineKeyboardButton(text=keyboard_text["lang"][lang], callback_data="change_lang")],
        [InlineKeyboardButton(text=back_text[lang], callback_data="back")]
    ]

    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})
