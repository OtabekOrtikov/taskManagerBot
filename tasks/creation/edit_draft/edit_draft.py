from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user_lang
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.escape_markdown import escape_markdown_v2
from utils.priority_parser import parse_priority

async def edit_draft_task(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    data = await state.get_data()
    task_title = data.get("task_title")
    task_description = data.get("task_description")
    start_date = data.get("start_date")
    due_date = data.get("due_date")
    task_assignee_id = data.get("task_assignee_id")
    priority_id = data.get("priority")
    priority = await parse_priority(priority_id, lang)


    db = get_db_pool()

    async with db.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", task_assignee_id)

    keyboard = []

    worker_name = escape_markdown_v2(worker['fullname'])
    worker_phone = worker['phone_number']

    if lang == 'en':
        send_text = (
            f"Task title: {task_title}\n"
            f"Task description: {task_description}\n"
            f"Start date: {start_date}\n"
            f"Due date: {due_date}\n"
            f"Assignee: {worker_name}\n"
            f"Phone number: {worker_phone}\n"
            f"Priority: {priority}\n\n"
            f"Please choose what you want to edit."
        )
        keyboard = [
            [InlineKeyboardButton(text="Task title", callback_data="edit_draft_title"), InlineKeyboardButton(text="Task description", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Date", callback_data="edit_draft_date"), InlineKeyboardButton(text="Priority", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Create task", callback_data="task_confirm"), InlineKeyboardButton(text="Cancel task creation", callback_data="back_to_main_menu")]
        ]
    elif lang == 'ru':
        send_text = (
            f"Название задания: {task_title}\n"
            f"Описание задания: {task_description}\n"
            f"Дата начала: {start_date}\n"
            f"Дата окончания: {due_date}\n"
            f"Исполнитель: {worker_name}\n"
            f"Номер телефона: {worker_phone}\n"
            f"Приоритет: {priority}\n\n"
            f"Вся информация верна?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Название задания", callback_data="edit_draft_title"), InlineKeyboardButton(text="Описание задания", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Дата", callback_data="edit_draft_date"), InlineKeyboardButton(text="Приоритет", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Создать задание", callback_data="task_confirm"), InlineKeyboardButton(text="Отменить создание задания", callback_data="back_to_main_menu")]
        ]
    elif lang == 'uz':
        send_text = (
            f"Vazifa nomi: {task_title}\n"
            f"Vazifa tavsifi: {task_description}\n"
            f"Boshlanish sanasi: {start_date}\n"
            f"Tugash sanasi: {due_date}\n"
            f"Ijrochi: {worker_name}\n"
            f"Telefon raqami: {worker_phone}\n"
            f"Ustuvorlik: {priority}\n\n"
            f"Bu ma'lumotlar to'g'ri mi?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Vazifa nomi", callback_data="edit_draft_title"), InlineKeyboardButton(text="Vazifa tavsifi", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Sana", callback_data="edit_draft_date"), InlineKeyboardButton(text="Ustuvorlik", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Vazifa yaratish", callback_data="task_confirm"), InlineKeyboardButton(text="Vazifa yaratishni bekor qilish", callback_data="back_to_main_menu")]
        ]
        
    await callback.message.edit_text(send_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)


async def edit_draft_task_msg(message: types.Message, state: FSMContext):
    
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    data = await state.get_data()
    task_title = data.get("task_title")
    task_description = data.get("task_description")
    start_date = data.get("start_date")
    due_date = data.get("due_date")
    task_assignee_id = data.get("task_assignee_id")
    priority_id = data.get("priority")
    priority = await parse_priority(priority_id, lang)


    db = get_db_pool()

    async with db.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", task_assignee_id)

    keyboard = []

    worker_name = escape_markdown_v2(worker['fullname'])
    worker_phone = worker['phone_number']

    if lang == 'en':
        send_text = (
            f"Task title: {task_title}\n"
            f"Task description: {task_description}\n"
            f"Start date: {start_date}\n"
            f"Due date: {due_date}\n"
            f"Assignee: {worker_name}\n"
            f"Phone number: {worker_phone}\n"
            f"Priority: {priority}\n\n"
            f"Please choose what you want to edit."
        )
        keyboard = [
            [InlineKeyboardButton(text="Task title", callback_data="edit_draft_title"), InlineKeyboardButton(text="Task description", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Date", callback_data="edit_draft_date"), InlineKeyboardButton(text="Priority", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Create task", callback_data="task_confirm"), InlineKeyboardButton(text="Cancel task creation", callback_data="back_to_main_menu")]
        ]
    elif lang == 'ru':
        send_text = (
            f"Название задания: {task_title}\n"
            f"Описание задания: {task_description}\n"
            f"Дата начала: {start_date}\n"
            f"Дата окончания: {due_date}\n"
            f"Исполнитель: {worker_name}\n"
            f"Номер телефона: {worker_phone}\n"
            f"Приоритет: {priority}\n\n"
            f"Вся информация верна?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Название задания", callback_data="edit_draft_title"), InlineKeyboardButton(text="Описание задания", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Дата", callback_data="edit_draft_date"), InlineKeyboardButton(text="Приоритет", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Создать задание", callback_data="task_confirm"), InlineKeyboardButton(text="Отменить создание задания", callback_data="back_to_main_menu")]
        ]
    elif lang == 'uz':
        send_text = (
            f"Vazifa nomi: {task_title}\n"
            f"Vazifa tavsifi: {task_description}\n"
            f"Boshlanish sanasi: {start_date}\n"
            f"Tugash sanasi: {due_date}\n"
            f"Ijrochi: {worker_name}\n"
            f"Telefon raqami: {worker_phone}\n"
            f"Ustuvorlik: {priority}\n\n"
            f"Bu ma'lumotlar to'g'ri mi?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Vazifa nomi", callback_data="edit_draft_title"), InlineKeyboardButton(text="Vazifa tavsifi", callback_data="edit_draft_description")],
            [InlineKeyboardButton(text="Sana", callback_data="edit_draft_date"), InlineKeyboardButton(text="Ustuvorlik", callback_data="edit_draft_priority")],
            [InlineKeyboardButton(text="Vazifa yaratish", callback_data="task_confirm"), InlineKeyboardButton(text="Vazifa yaratishni bekor qilish", callback_data="back_to_main_menu")]
        ]
        
    send_message = await message.answer(send_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=send_message.message_id)