from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from config import PAGE_SIZE
from database.db_utils import get_db_pool, get_user
from btns import back_to_main, next_page
from states import TaskCreation

from utils.date_function import parse_and_validate_date

async def process_due_date(message: types.Message, state: FSMContext):
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

    keyboard = []
    send_text = {
        'en': f"So, you have set the task completion date from {start_date} to {due_date} now, please select the worker who should complete this task.\n\nP.s. You can enter the worker's phone number in the format \"+998aabbbccdd\" to find it.",
        'ru': f"Итак, вы установили дату завершения задачи с {start_date} на {due_date}, теперь выберите сотрудника, который должен выполнить эту задачу.\n\nP.s. Вы можете ввести номер телефона сотрудника в формате \"+998aabbbccdd\", чтобы найти его.",
        'uz': f"Demak, siz vazifani yakunlash sanasini {start_date} dan {due_date} ga sozladingiz, endi ushbu vazifani bajarishi kerak bo'lgan xodimni tanlang.\n\nP.s. Siz uning telefon raqamini \"+998aabbbccdd\" formatda kiritsangiz, uni topishingiz mumkin."
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