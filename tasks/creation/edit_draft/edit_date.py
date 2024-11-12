from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user, get_user_lang
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from states import DraftChanges
from tasks.creation.date_function import parse_and_validate_date
from tasks.creation.edit_draft.edit_draft import edit_draft_task_msg

async def edit_draft_date(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    start_date = data.get("start_date")
    due_date = data.get("due_date")
    priority_id = data.get("priority")

    send_text = {
        'en': f"Current dates:\nStart date: {start_date}\nDue date: {due_date}\n\nPlease select what you want to edit.",
        'ru': f"Текущие даты:\nДата начала: {start_date}\nДата завершения: {due_date}\n\nПожалуйста, выберите, что вы хотите изменить.",
        'uz': f"Joriy sanalar:\nBoshlash sanasi: {start_date}\nTugash sanasi: {due_date}\n\nIltimos, o'zgartirmoqchi bo'lganini tanlang."
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
    await state.set_state(DraftChanges.draft_start_date)

async def process_draft_start_date(message: types.Message, state: FSMContext):
    start_date_str = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    data = await state.get_data()
    priority_id = data.get("priority")

    keyboard_text = {
        'en': "Cancel",
        'ru': "Отменить",
        'uz': "Bekor qilish"
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=keyboard_text[lang], callback_data=f"task_priority_{priority_id}")]])

    try:
        start_date = parse_and_validate_date(start_date_str)
    except ValueError as e:
        if lang == 'en':
            await message.answer("Invalid date format. Please enter the start date in the format: **dd.mm** or **dd.mm.yy**", parse_mode="Markdown", reply_markup=keyboard)
        elif lang == 'ru':
            await message.answer("Неверный формат даты. Пожалуйста, введите дату начала в формате: **дд.мм** или **дд.мм.гг**", parse_mode="Markdown", reply_markup=keyboard)
        elif lang == 'uz':
            await message.answer("Noto'g'ri sana formati. Iltimos, boshlash sanasini quyidagi formatda kiriting: **kk.oy** yoki **kk.oy.yy**", parse_mode="Markdown", reply_markup=keyboard)
        return
    
    await state.update_data(start_date=start_date)

    if lang == 'en':
        send_text = f"Great, you set date for start date: {start_date}. Now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**"
    elif lang == 'ru':
        send_text = f"Отлично, вы установили дату начала: {start_date}. Теперь введите дату завершения задачи в формате: **дд.мм** или **дд.мм.гг**"
    elif lang == 'uz':
        send_text = f"Ajoyib, siz boshlash sanasini {start_date}'ga sozladingiz. Endi vazifaning tugash sanasini quyidagi formatda kiriting: **kk.oy** yoki **kk.oy.yy**"

    send_message = await message.answer(send_text, parse_mode="Markdown", reply_markup=keyboard)
    await state.update_data(main_menu_message_id=send_message.message_id)
    await state.set_state(DraftChanges.draft_due_date)

async def process_draft_due_date(message: types.Message, state: FSMContext):
    due_date_str = message.text
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    data = await state.get_data()
    try:
        # Process start and due dates
        start_date = parse_and_validate_date(data.get("start_date"))
        due_date = parse_and_validate_date(due_date_str, reference_date=datetime.strptime(start_date, "%d.%m.%Y"))
    except ValueError as e:
        # Send error message to user based on language
        error_messages = {
            'en': str(e),
            'ru': f"Неверный формат или дата вне диапазона. {e}",
            'uz': "Xato format yoki sana chegaradan tashqarida."
        }
        await message.answer(error_messages[lang], parse_mode="Markdown")
        return
    
    await state.update_data(due_date=due_date)

    send_text = {
        "en": f"Great! You have set the task completion date from {start_date} to {due_date} now.",
        "ru": f"Отлично! Вы установили дату завершения задачи с {start_date} на {due_date} теперь.",
        "uz": f"Ajoyib! Siz vazifa yakunlash sanasini {start_date} dan {due_date} ga sozladingiz."
    }

    await message.answer(send_text[lang])
    await edit_draft_task_msg(message, state)