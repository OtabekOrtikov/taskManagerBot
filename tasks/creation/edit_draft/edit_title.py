from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user_lang
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from states import DraftChanges
from tasks.creation.edit_draft.edit_draft import edit_draft_task_msg


async def edit_draft_title(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    task_title = data.get("task_title")
    priority_id = data.get("priority")

    send_text = {
        'en': f"Current task title: {task_title}\n\nPlease enter the new task title.",
        'ru': f"Текущее название задачи: {task_title}\n\nПожалуйста, введите новое название задачи.",
        'uz': f"Joriy vazifa sarlavhasi: {task_title}\n\nIltimos, yangi vazifa sarlavhasini kiriting."
    }

    keyboard_text = {
        'en': "Cancel",
        'ru': "Отменить",
        'uz': "Bekor qilish"
    }

    keyboard = [
        [InlineKeyboardButton(text=keyboard_text[lang], callback_data=f"task_priority_{priority_id}")]
    ]

    await callback.message.edit_text(send_text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(DraftChanges.draft_title)

async def process_draft_title(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(task_title=title)
    lang = await get_user_lang(message.from_user.id)

    text = {
        "en": "Great! New task title has been saved.",
        "ru": "Отлично! Новое название задачи сохранено.",
        "uz": "Ajoyib! Yangi vazifa sarlavhasi saqlandi."
    }

    await message.answer(text[lang])
    await edit_draft_task_msg(message, state)