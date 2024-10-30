from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation
from utils.parse_date import parse_date

from utils.validation_date import validate_date

async def process_start_date(message: types.Message, state: FSMContext):
    start_date = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Validate start date format and range
    if not validate_date(start_date):
        # Define invalid date message based on the language
        if lang == 'en':
            error_text = "Invalid date format or date out of range. Please enter a start date in one of the following formats: **dd.mm**, **dd.mm.yy**, or **dd.mm.yyyy**, from today up to 01.01.2026."
        elif lang == 'ru':
            error_text = "Неверный формат даты или дата вне диапазона. Пожалуйста, введите дату начала в одном из следующих форматов: **дд.мм**, **дд.мм.гг** или **дд.мм.гггг**, начиная с сегодняшнего дня и до 01.01.2026."
        elif lang == 'uz':
            error_text = "Noto‘g‘ri sana formati yoki sana belgilangan chegaradan tashqarida. Iltimos, boshlanish sanasini quyidagi formatlarda kiriting: **kk.oo**, **kk.oo.yy** yoki **kk.oo.yyyy**, bugundan 01.01.2026 gacha."

        await message.answer(error_text, parse_mode="Markdown")
        return

    # Save the start date if valid
    await state.update_data(start_date=parse_date(start_date))
    keyboard = []

    # Prepare the next prompt based on the language
    if lang == 'en':
        send_text = "Great, now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**"
    elif lang == 'ru':
        send_text = "Отлично, теперь введите дату окончания задачи в формате: **дд.мм** или **дд.мм.гг**"
    elif lang == 'uz':
        send_text = "Ajoyib, endi vazifa tugash sanasini quyidagi formatda kiriting: **kk.oo** yoki **kk.oo.yy**"
    
    keyboard.append([back_to_main[lang]])
    await message.answer(send_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=message.message_id)
    await state.set_state(TaskCreation.due_date)
