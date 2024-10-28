from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user
from btns import back_to_settings
from menu.main_menu import navigate_to_main_menu
from states import UserChanges

async def edit_fullname(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    if lang == 'ru':
        text = "Введите новое имя:"
    elif lang == 'uz':
        text = "Yangi ismingizni kiriting:"

    keyboard = [
        [back_to_settings[lang]]
    ]

    send_message = await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(UserChanges.fullname)

async def changing_fullname(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET fullname = $1 WHERE user_id = $2", message.text, user_id)

    text = "Имя успешно изменено." if lang == 'ru' else "Ism muvaffaqiyatli o'zgartirildi." if lang == 'uz' else "Name successfully changed."

    await message.answer(text)
    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)