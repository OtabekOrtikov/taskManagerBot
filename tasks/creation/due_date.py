from aiogram import types
from aiogram.fsm.context import FSMContext
from config import PAGE_SIZE
from database.db_utils import get_db_pool, get_user
from btns import back_to_main, next_page
from states import TaskCreation
from datetime import datetime
from utils.parse_date import parse_date

async def process_due_date(message: types.Message, state: FSMContext):
    due_date_text = message.text
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    # Retrieve and parse start_date from state
    data = await state.get_data()
    start_date_text = data.get("start_date")
    if not start_date_text:
        await message.answer("Start date is not set. Please set the start date before setting the due date.")
        return

    try:
        start_date = parse_date(start_date_text)
    except ValueError as e:
        await message.answer(f"Invalid start date. Please enter a valid start date before setting the due date. {e}")
        return

    # Parse and validate the due date
    try:
        due_date = parse_date(due_date_text)
    except ValueError:
        # Error message based on language if due date format is invalid
        error_text = {
            'en': "Invalid date format or date out of range. Please enter a due date in one of the following formats: **dd.mm** or **dd.mm.yy**.",
            'ru': "Неверный формат даты или дата вне диапазона. Пожалуйста, введите дату окончания в одном из следующих форматов: **дд.мм** или **дд.мм.гг**.",
            'uz': "Noto‘g‘ri sana formati yoki sana belgilangan chegaradan tashqarida. Iltimos, tugash sanasini quyidagi formatlarda kiriting: **kk.oo** yoki **kk.oo.yy**."
        }
        await message.answer(error_text[lang], parse_mode="Markdown")
        return

    # Ensure that due date is after start date
    if due_date <= start_date:
        error_text = {
            'en': "The due date must be after the start date. Please enter a valid due date.",
            'ru': "Дата окончания должна быть после даты начала. Пожалуйста, введите корректную дату окончания.",
            'uz': "Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak. Iltimos, tugash sanasini to‘g‘ri kiriting."
        }
        await message.answer(error_text[lang], parse_mode="Markdown")
        return
    
    # Update state with valid due date
    await state.update_data(due_date=parse_date(due_date_text))

    # Prepare message for worker selection
    keyboard = []
    send_text = {
        'en': "Well, now, please select the worker who should complete this task.\n\nP.s. You can enter the worker's phone number in the format \"+998aabbbccdd\" to find it.",
        'ru': "Что ж, теперь, пожалуйста, выберите сотрудника, который должен выполнить это задание.\n\nP.s. Вы можете ввести номер телефона сотрудника в формате \"+998aabbbccdd\", чтобы найти его.",
        'uz': "Xo'sh, endi, iltimos, ushbu vazifani bajarishi kerak bo'lgan xodimni tanlang.\n\nP.s. Siz uni qidirish uchun xodimning telefon raqamini \"+998aabbccdd\" formatida yozishingiz mumkin."
    }

    db = get_db_pool()

    async with db.acquire() as connection:
        # Fetch workers based on user role and company affiliation
        if user['role_id'] == 1:
            workers = await connection.fetch("SELECT * FROM users WHERE role_id != 1 AND company_id = $1", user['company_id'])
        else:
            workers = await connection.fetch("SELECT * FROM users WHERE role_id != 1 AND company_id = $1 AND department_id = $2", user['company_id'], user['department_id'])

    total_workers = len(workers)

    # Handle case where no workers are found
    if total_workers == 0:
        error_text = {
            'en': "You don't have any workers in your company. Please add workers to your company first.",
            'ru': "У вас нет сотрудников в вашей компании. Пожалуйста, сначала добавьте сотрудников в вашу компанию.",
            'uz': "Sizning kompaniyangizda hech qanday xodimlar yo‘q. Iltimos, avval kompaniyangizga xodim qo‘shing."
        }
        await message.answer(error_text[lang])
        return
    
    total_pages = (total_workers + PAGE_SIZE - 1) // PAGE_SIZE
    current_workers = workers[:PAGE_SIZE]

    # Create keyboard buttons for workers
    for worker in current_workers:
        keyboard.append([types.InlineKeyboardButton(text=worker['fullname'], callback_data=f"task_worker_{worker['id']}")])

    # Add pagination if there are multiple pages of workers
    if total_pages > 1:
        keyboard.append([types.InlineKeyboardButton(text=next_page[lang], callback_data=f"task_workers_page_2")])
    keyboard.append([back_to_main[lang]])

    await message.answer(send_text[lang], reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=message.message_id+1)
    await state.set_state(TaskCreation.task_assignee_phone)
