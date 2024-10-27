from aiogram.fsm.context import FSMContext
from db_utils import get_user_lang
from aiogram import types

from states import DepartmentCreation

async def continue_department_creation(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)

    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id != callback.message.message_id + 1:
        await callback.answer(f"This button is no longer active.", show_alert=True)
        return

    if lang == 'ru':
        prompt_text = "Введите название следующего отдела."
    else:
        prompt_text = "Keyingi bo‘lim nomini kiriting."

    await callback.message.edit_text(prompt_text)
    await state.set_state(DepartmentCreation.department_name)