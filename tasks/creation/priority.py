from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user_lang
from states import TaskCreation
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.escape_markdown import escape_markdown_v2
from utils.priority_parser import parse_priority

async def progress_task_priority(callback: types.CallbackQuery, state: FSMContext):
    last_button_message_id = (await state.get_data()).get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    priority_id = callback.data.split("_")[-1]
    await state.update_data(priority=priority_id)
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    priority = await parse_priority(priority_id, lang)

    await state.update_data(priority=priority)

    data = await state.get_data()
    task_title = data.get("task_title")
    task_description = data.get("task_description")
    start_date = data.get("start_date")
    due_date = data.get("due_date")
    task_assignee_id = data.get("task_assignee_id")


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
            f"Is this information correct?"
        )
        keyboard = [
            [InlineKeyboardButton(text="Yes", callback_data="task_confirm"), InlineKeyboardButton(text="Edit information", callback_data="edit_draft_task")],
            [InlineKeyboardButton(text="Cancel", callback_data="back_to_main_menu")]
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
            [InlineKeyboardButton(text="Да", callback_data="task_confirm"), InlineKeyboardButton(text="Изменить информацию", callback_data="edit_draft_task")],
            [InlineKeyboardButton(text="Отменить", callback_data="back_to_main_menu")]
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
            [InlineKeyboardButton(text="Ha", callback_data="task_confirm"), InlineKeyboardButton(text="Ma'lumotni o'zgartirish", callback_data="edit_draft_task")],
            [InlineKeyboardButton(text="Bekor qilish", callback_data="back_to_main_menu")]
        ]

    await callback.message.edit_text(send_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskCreation.task_confirm)
