from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation

from utils.date_function import parse_and_validate_date

async def set_today_date(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    # Verify that the callback message is still active
    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    # Set start date to today's date in 'dd.mm' format and validate it
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    start_date = parse_and_validate_date("today")  # Parses as 'dd.mm.yyyy' based on current or next year

    # Update state with the validated start date
    await state.update_data(start_date=start_date)

    # Prepare the keyboard and send a confirmation message in the user's language
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]])

    send_texts = {
        'en': "Start date set to today. Now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**",
        'ru': "Дата начала установлена на сегодня. Теперь введите дату завершения задачи в формате: **дд.мм** или **дд.мм.гг**",
        'uz': "Boshlash sanasi bugungi kunga sozlandi. Endi vazifaning tugash sanasini quyidagi formatda kiriting: **kk.oy** yoki **kk.oy.yy**"
    }
    send_text = send_texts.get(lang, send_texts['en'])

    # Edit the callback message and update the state
    await callback.message.edit_text(send_text, parse_mode="Markdown", reply_markup=keyboard)
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskCreation.due_date)
