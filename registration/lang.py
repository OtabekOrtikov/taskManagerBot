from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool
from states import RegistrationStates

async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET lang = $1 WHERE user_id = $2", lang, user_id)

    # Move to registration state
    if lang == 'ru':
        await callback.message.answer("Для регистрации введите ваше имя.")
    elif lang == 'uz':
        await callback.message.answer("Ro'yxatdan o'tish uchun ismingizni kiriting.")

    await state.set_state(RegistrationStates.fullname)