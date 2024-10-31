from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PAGE_SIZE
from database.db_utils import get_user, get_db_pool
from btns import next_page, back_page

async def list_worker_tasks(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    db_pool = get_db_pool()
    worker_id = int(callback.data.split("_")[2])
    page = int(callback.data.split("_")[-1]) if len(callback.data.split("_")) > 3 else 1
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    async with db_pool.acquire() as connection:
        tasks = await connection.fetch("""
                                    SELECT 
                                        t.id as task_id,
										t.task_title
                                    FROM 
                                        task t 
                                    JOIN users u 
                                    ON t.task_assignee_id = u.id 
                                    WHERE t.task_assignee_id = $1 
                                    ORDER BY priority
                                """, worker_id)
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
    
    text = {
        "en": f"Here are the {worker['fullname']}'s tasks:",
        "ru": f"Вот задания {worker['fullname']}:",
        "uz": f"{worker['fullname']}ning vazifalari:"
    }

    if not tasks:
        text = {
            "en": f"{worker['fullname']} has no tasks.",
            "ru": f"У {worker['fullname']} нет заданий.",
            "uz": f"{worker['fullname']}ning vazifalari yo'q."
        }
        await callback.message.edit_text(text[lang])
        return
    
    keyboard = []

    total_tasks = len(tasks)
    total_pages = total_tasks // PAGE_SIZE + 1 if total_tasks % PAGE_SIZE != 0 else total_tasks // PAGE_SIZE

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    for task in tasks[start:end]:
        keyboard.append(
            [InlineKeyboardButton(
                text=task['task_title'],
                callback_data=f"task_info_{task['task_id']}"
            )]
        )

    if total_pages > 1:
        if page > 1:
            keyboard.append(
                [InlineKeyboardButton(
                    text=back_page[lang],
                    callback_data=f"list_worker_tasks_{worker_id}_{page - 1}"
                )]
            )
        if page < total_pages:
            keyboard.append(
                [InlineKeyboardButton(
                    text=next_page[lang],
                    callback_data=f"list_worker_tasks_{worker_id}_{page + 1}"
                )]
            )

    keyboard_text = {
        "en": f"🔙Back to worker settings",
        "ru": f"🔙Назад к настройкам работника",
        "uz": f"🔙Ishchi sozlamalariga qaytish"
    }

    keyboard.append(
        [InlineKeyboardButton(
            text=keyboard_text[lang],
            callback_data=f"show_worker_{worker_id}"
        )]
    )

    # Check if content has changed
    await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
    await state.update_data(main_menu_message_id=callback.message.message_id)
