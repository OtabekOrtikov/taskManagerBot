from aiogram.fsm.context import FSMContext
from btns import back_to_settings
from database.db_utils import get_db_pool, get_user
from menu.main_menu import navigate_to_main_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

async def edit_lang(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    text = "Выберите язык:" if lang == 'ru' else "Tilni tanlang:" if lang == 'uz' else "Choose a language:"

    keyboard = [
        [InlineKeyboardButton(text="Русский", callback_data="change_lang_ru"), InlineKeyboardButton(text="O'zbekcha", callback_data="change_lang_uz")],
        [back_to_settings[lang]]
    ]
    send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=send_message.message_id)

async def changing_lang(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    lang = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    if lang == user_lang:
        if lang == 'ru':
            await callback.answer("Вы уже используете русский язык.")
        elif lang == 'uz':
            await callback.answer("Siz o'zbek tilida foydalanmoqdasiz.")
        return

    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET lang = $1 WHERE user_id = $2", lang, user_id)

    await state.clear()
    if lang == 'ru':
        await callback.message.answer("Язык успешно изменен.")
    elif lang == 'uz':
        await callback.message.answer("Til muvaffaqiyatli o'zgartirildi.")
    await navigate_to_main_menu(user_id, callback.message.chat.id, state)