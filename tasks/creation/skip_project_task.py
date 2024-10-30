from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation

async def skip_creation_ptask(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if lang == "en":
        text = f"Great, you are creating a task for an employee of your company.\n\nPlease enter the task name. Maximum 30 characters."
    elif lang == "ru":
        text = f"Отлично, вы создаете задачу для сотрудника вашей компании.\n\nВведите название задачи. Максимум 30 символов."
    elif lang == "uz":
        text = f"Ajoyib, siz kompaniyangizning xodimi uchun vazifa yaratmoqdasiz.\n\nVazifa nomini kiriting. Maksimum 30 belgi."
    
    send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]]))
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(TaskCreation.task_title)