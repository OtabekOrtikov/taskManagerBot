from aiogram import types
from aiogram.fsm.context import FSMContext

from menu.main_menu import navigate_to_main_menu

async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    """Handles navigating back to the main menu, using role-based logic."""
    await callback.message.delete()  # Optionally delete the previous message
    await navigate_to_main_menu(callback.from_user.id, callback.message.chat.id, state)  # Go to main menu