from aiogram import types
from aiogram.fsm.context import FSMContext

from qarz_utils.main_menu import main_menu
from qarz_utils.basic_texts import noactive_btn
from qarz_database.db_utils import get_user_lang

async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_message_id")
    lang = await get_user_lang(callback.from_user.id)

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    """Handles navigating back to the main menu, using role-based logic."""
    await callback.message.delete()
    await state.clear()
    await main_menu(callback.from_user.id, callback.message.chat.id, state)  # Go to main menu