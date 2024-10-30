from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from database.db_utils import get_user_lang
from states import TaskCreation
from btns import back_to_main


async def set_today_date(callback: types.CallbackQuery, state: FSMContext):
    message_date = await state.get_data()
    last_button_message_id = message_date.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer(f"This button is no longer active. {last_button_message_id} {callback.message.message_id}")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    today = datetime.now().strftime("%d.%m.%Y")

    # Save start date in state as a string
    await state.update_data(start_date=today)

    if lang == 'en':
        send_text = "Great, now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**"
    elif lang == 'ru':
        send_text = "Отлично, теперь введите дату окончания задачи в формате: **дд.мм** или **дд.мм.гг**"
    elif lang == 'uz':
        send_text = "Ajoyib, endi vazifa tugash sanasini quyidagi formatda kiriting: **kk.oo** yoki **kk.oo.yy**"
    
    await callback.message.edit_text(send_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]]))
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskCreation.due_date)