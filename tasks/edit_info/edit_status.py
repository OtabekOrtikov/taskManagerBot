from aiogram.fsm.context import FSMContext
from config import API_TOKEN
from database.db_utils import get_db_pool, get_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, Bot

from tasks.task_info import task_info

bot = Bot(token=API_TOKEN)

async def start_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Task started.",
        'ru': "Задача начата.",
        'uz': "Vazifa boshlandi."
    }

    async with db.acquire() as conn:
        await conn.execute("UPDATE task SET status = 'In progress', started_at = CURRENT_TIMESTAMP WHERE id = $1", task_id)
    
    await callback.answer(text[lang])
    await task_info(callback, state)
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def finish_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Task finished.",
        'ru': "Задача завершена.",
        'uz': "Vazifa yakunlandi."
    }

    async with db.acquire() as conn:
        await conn.execute("UPDATE task SET status = 'Finished', finished_at = CURRENT_TIMESTAMP WHERE id = $1", task_id)
        task = await conn.fetchrow("SELECT task_title, task_owner_id FROM task WHERE id = $1", task_id)
        task_owner_id = await conn.fetchrow("SELECT task_owner_id FROM task WHERE id = $1", task_id)
        owner = await conn.fetchrow("SELECT user_id, lang FROM users WHERE id = $1", task_owner_id['task_owner_id'])
    
    owner_text = {
        'en': f"User {user['fullname']} has finished the task \"{task['task_title']}\".",
        'ru': f"Пользователь {user['fullname']} завершил задачу \"{task['task_title']}\".",
        'uz': f"Foydalanuvchi {user['fullname']} vazifani \"{task['task_title']}\" yakunladi."
    }
    await callback.answer(text[lang])
    await task_info(callback, state)
    await bot.send_message(owner['user_id'], owner_text[owner['lang']])
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def cancel_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Are you sure you want to cancel this task?",
        'ru': "Вы уверены, что хотите отменить эту задачу?",
        'uz': "Ushbu vazifani bekor qilmoqchimisiz?"
    }

    keyboard = [
        [InlineKeyboardButton(text="Yes", callback_data=f"confirm_cancel_task_{task_id}"), InlineKeyboardButton(text="No", callback_data=f"task_info_{task_id}")]
    ]

    await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def confirm_cancel_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Task cancelled.",
        'ru': "Задача отменена.",
        'uz': "Vazifa bekor qilindi."
    }

    async with db.acquire() as conn:
        await conn.execute("UPDATE task SET status = 'Cancelled', canceled_at = CURRENT_TIMESTAMP WHERE id = $1", task_id)
    
    await callback.answer(text[lang])
    await task_info(callback, state)
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def pause_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Task paused.",
        'ru': "Задача приостановлена.",
        'uz': "Vazifa to‘xtatildi."
    }

    async with db.acquire() as conn:
        await conn.execute("UPDATE task SET status = 'Paused', paused_at = CURRENT_TIMESTAMP WHERE id = $1", task_id)
    
    await callback.answer(text[lang])
    await task_info(callback, state)
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def continue_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        'en': "Task continued.",
        'ru': "Задача продолжена.",
        'uz': "Vazifa davom ettirildi."
    }

    async with db.acquire() as conn:
        await conn.execute("UPDATE task SET status = 'In progress', continued_at = CURRENT_TIMESTAMP WHERE id = $1", task_id)
    
    await callback.answer(text[lang])
    await task_info(callback, state)
    await state.update_data(main_menu_message_id=callback.message.message_id)
