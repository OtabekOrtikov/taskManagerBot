from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user_lang
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from states import DraftChanges
from tasks.creation.edit_draft.edit_draft import edit_draft_task_msg
from utils.priority_parser import parse_priority

async def edit_draft_priority(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    priority_id = data.get("priority")
    priority = await parse_priority(priority_id, lang)

    send_text = {
        'en': f"Current priority: {priority}\n\nPlease select the new priority.",
        'ru': f"Текущий приоритет: {priority}\n\nПожалуйста, выберите новый приоритет.",
        'uz': f"Joriy ustuvorlik: {priority}\n\nIltimos, yangi ustuvorlikni tanlang."
    }

    keyboard_text = {
        'en': "Cancel",
        'ru': "Отменить",
        'uz': "Bekor qilish"
    }

    priority_btn = {
        "ru": InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Низкий", callback_data="task_priority_1"),
                InlineKeyboardButton(text="Средний", callback_data="task_priority_2"),
                InlineKeyboardButton(text="Высокий", callback_data="task_priority_3")],
                [InlineKeyboardButton(text=keyboard_text['ru'], callback_data=f"task_priority_{priority_id}")]
            ]),
            "uz": InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Past", callback_data="task_priority_1"),
                InlineKeyboardButton(text="O'rta", callback_data="task_priority_2"),
                InlineKeyboardButton(text="Yuqori", callback_data="task_priority_3")],
                [InlineKeyboardButton(text=keyboard_text['uz'], callback_data=f"task_priority_{priority_id}")]
            ]),
            "en": InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Low", callback_data="task_priority_1"),
                InlineKeyboardButton(text="Medium", callback_data="task_priority_2"),
                InlineKeyboardButton(text="High", callback_data="task_priority_3")],
                [InlineKeyboardButton(text=keyboard_text['en'], callback_data=f"task_priority_{priority_id}")]
            ])
    }

    await callback.message.edit_text(send_text[lang], reply_markup=priority_btn[lang])
    await state.update_data(main_menu_message_id=callback.message.message_id)
