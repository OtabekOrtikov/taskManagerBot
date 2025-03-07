from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_db_pool
from qarz_utils.basic_texts import noactive_btn, user_data, back_text
from qarz_utils.btns import user_change_btn, back_btn
from qarz_states import ChangeUserData
from qarz_utils.main_menu import main_menu

async def edit_user_data(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    text = user_data(user)[lang]

    keyboard = user_change_btn[lang]

    send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})

async def change_user(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    data = callback.data.split("_")

    if data[1] == "name":
        text = {
            "ru": "💬 Введите новое имя",
            "uz": "💬 Yangi ismingizni kiriting",
            "oz": "💬 Янги исмингизни киритинг"
        }
        await state.set_state(ChangeUserData.user_name)
    elif data[1] == "phone":
        text = {
            "ru": "💬 Введите новый номер",
            "uz": "💬 Yangi raqamingizni kiriting",
            "oz": "💬 Янги рақамингизни киритинг"
        }
        await state.set_state(ChangeUserData.user_phone)
    elif data[1] == "birthday":
        text = {
            "ru": "💬 Введите новую дату рождения",
            "uz": "💬 Yangi tug'ilgan kuningizni kiriting",
            "oz": "💬 Янги туғилган кунингизни киритинг",
        }
        await state.set_state(ChangeUserData.user_birthday)
    else:
        text = {
            "ru": "⛔️ Ошибка",
            "uz": "⛔️ Xatolik",
            "oz": "⛔️ Хатолик"
        }

    keyboard = [[InlineKeyboardButton(text=back_text[lang], callback_data="change_user_data")]]
    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})

async def process_user_name(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    lang = user['lang']

    db = await get_db_pool()

    await db.execute("UPDATE users SET fullname = $1 WHERE user_id = $2", message.text, message.from_user.id)

    await message.answer("Имя успешно изменено")
    await main_menu(message.from_user.id, message.chat.id, state)

async def process_user_phone(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    lang = user['lang']

    db = await get_db_pool()

    await db.execute("UPDATE users SET phone_number = $1 WHERE user_id = $2", message.text, message.from_user.id)

    await message.answer("Номер успешно изменен")
    await main_menu(message.from_user.id, message.chat.id, state)

async def process_user_birthday(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    lang = user['lang']

    db = await get_db_pool()

    await db.execute("UPDATE users SET birthdate = $1 WHERE user_id = $2", message.text, message.from_user.id)

    await message.answer("Дата рождения успешно изменена")
    await main_menu(message.from_user.id, message.chat.id, state)