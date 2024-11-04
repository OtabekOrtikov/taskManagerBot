from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation

async def process_task_title(message: types.Message, state: FSMContext): 
    task_title = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]])

    if len(task_title) > 30:
        if lang == "en":
            text = "Task name is too long. Maximum 30 characters."
        elif lang == "ru":
            text = "Слишком длинное название задачи. Максимум 30 символов."
        elif lang == "uz":
            text = "Vazifa nomi juda uzun. Maksimum 30 belgi."
        
        await message.answer(text, reply_markup=keyboard)
        return
    
    await state.update_data(task_title=task_title)

    if lang == 'en':
        send_text = "Very good, now please enter the task description."
    elif lang == 'ru':
        send_text = "Отлично, теперь введите описание задачи."
    elif lang == 'uz':
        send_text = "Ajoyib, endi vazifa tavsifini kiriting."

    await message.answer(send_text, reply_markup=keyboard)
    await state.update_data(main_menu_message_id=message.message_id+1)
    await state.set_state(TaskCreation.task_description)