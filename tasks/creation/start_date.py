from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation

from utils.date_function import parse_and_validate_date

async def process_start_date(message: types.Message, state: FSMContext):
    start_date_str = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]])


    start_date = parse_and_validate_date(start_date_str)
    
    await state.update_data(start_date=start_date)

    if lang == 'en':
        send_text = f"Great, you set date for start date: {start_date}. Now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**"
    elif lang == 'ru':
        send_text = f"Отлично, вы установили дату начала: {start_date}. Теперь введите дату завершения задачи в формате: **дд.мм** или **дд.мм.гг**"
    elif lang == 'uz':
        send_text = f"Ajoyib, siz boshlash sanasini {start_date}'ga sozladingiz. Endi vazifaning tugash sanasini quyidagi formatda kiriting: **kk.oy** yoki **kk.oy.yy**"

    await message.answer(send_text, parse_mode="Markdown", reply_markup=keyboard)
    await state.update_data(main_menu_message_id=message.message_id+1)
    await state.set_state(TaskCreation.due_date)