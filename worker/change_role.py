from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PAGE_SIZE
from database.db_utils import get_user, get_db_pool
from btns import next_page, back_page
from worker.show_worker import show_worker

async def change_user_role(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    # Extract worker ID from callback data
    worker_id = int(callback.data.split("_")[-1])

    async with db_pool.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        
        if worker['role_id'] == 2:
            await connection.execute("UPDATE users SET role_id = 3 WHERE id = $1", worker_id)
        else:
            await connection.execute("UPDATE users SET role_id = 2 WHERE id = $1", worker_id)

    await callback.answer("User role has been changed.")
    await show_worker(callback, state)