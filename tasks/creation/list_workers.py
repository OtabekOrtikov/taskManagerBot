from aiogram import types
from aiogram.fsm.context import FSMContext
from config import PAGE_SIZE
from database.db_utils import get_user, get_db_pool
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states import TaskCreation
from btns import back_to_main, next_page, back_page

async def process_list_workers(callback: types.CallbackQuery, state: FSMContext):
    last_button_message_id = (await state.get_data()).get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.message.answer("This button is no longer active.")
        return

    page = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    db = get_db_pool()
    
    data = await state.get_data()

    project_id = data.get("project_id") if data.get("project_id") else None

    async with db.acquire() as connection:
        # Fetch workers based on user role and company affiliation
        if project_id != None:
            if user['role_id'] == 1:
                workers = await connection.fetch("SELECT * FROM users WHERE role_id != 1 AND company_id = $1", user['company_id'])
            else:
                workers = await connection.fetch("SELECT * FROM users WHERE role_id != 1 AND company_id = $1 AND department_id = $2", user['company_id'], user['department_id'])
        else:
            workers = await connection.fetch("SELECT * FROM users WHERE role_id != 1")

    total_workers = len(workers)
    total_pages = total_workers // PAGE_SIZE + 1 if total_workers % PAGE_SIZE != 0 else total_workers // PAGE_SIZE

    if total_workers == 0:
        if lang == 'en':
            send_text = "You don't have any workers in your company. Please add workers to your company first."
        elif lang == 'ru':
            send_text = "У вас нет сотрудников в вашей компании. Пожалуйста, сначала добавьте сотрудников в вашу компанию."
        elif lang == 'uz':
            send_text = "Sizning kompaniyangizda hech qanday xodimlar yo'q. Iltimos, avval kompaniyangizga xodim qo'shing."

        await callback.message.answer(send_text)
        return
    
    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1
    
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    keyboard = []

    for worker in workers[start:end]:
        keyboard.append([InlineKeyboardButton(text=worker['fullname'], callback_data=f"task_worker_{worker['id']}")])

    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"task_workers_page_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[lang], callback_data=f"task_workers_page_{page + 1}")])

    keyboard.append([back_to_main[user['lang']]])

    if lang == 'en':
        send_text = f"Well, now, please select the worker who should complete this task.\nPage: {page}\n\nP.s. You can enter the worker's phone number in the format \"+998aabbbccdd\" to find it."
    elif lang == 'ru':
        send_text = f"Что ж, теперь, пожалуйста, выберите сотрудника, который должен выполнить это задание.\nСтраница: {page}\n\nP.s. Вы можете ввести номер телефона сотрудника в формате \"+998aabbbccdd\", чтобы найти его."
    elif lang == 'uz':
        send_text = f"Xo'sh, endi, iltimos, ushbu vazifani bajarishi kerak bo'lgan xodimni tanlang.\nSahifa: {page}\n\nP.s. Siz uni qidirish uchun xodimning telefon raqamini \"+998aabbccdd\" formatida yozishingiz mumkin."

    await callback.message.edit_text(send_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskCreation.task_assignee_phone)