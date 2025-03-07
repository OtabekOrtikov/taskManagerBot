from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_db_pool, get_user_lang
from aiogram import types

from qarz_debt.debt_ask import ask_approve_debt
from qarz_utils.main_menu import main_menu
from qarz_utils.basic_texts import noactive_btn, registration_complete

async def process_accept_rules(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    await callback.message.delete()
    db_pool = await get_db_pool()
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET accepted_rules = $1 WHERE user_id = $2", True, user_id)
    await callback.message.answer(registration_complete[lang])
    if message_data.get("waiting_for_approve"):
        await ask_approve_debt(message_data.get("waiting_for_approve"), message_data.get("waiting_for_approve_type"), callback.message, state)
    else:    
        await state.clear()
        await main_menu(user_id, callback.message.chat.id, state)