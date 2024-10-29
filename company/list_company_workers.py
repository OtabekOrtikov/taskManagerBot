from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, back_page, next_page

from config import PAGE_SIZE

async def list_workers(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    # Extract current page from callback data
    data = callback.data.split("_")
    page = int(data[2]) if len(data) > 2 else 1

    async with db_pool.acquire() as connection:
        # Fetch all workers for pagination
        workers = await connection.fetch("SELECT * FROM users WHERE company_id = $1", user['company_id'])
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])

    # Calculate total pages
    total_workers = len(workers)
    total_pages = (total_workers + PAGE_SIZE - 1) // PAGE_SIZE

    # Adjust the page if out of bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Paginate workers
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    current_workers = workers[start:end]

    # Build message text and keyboard
    if lang == 'en':
        text = f"Workers of {company['company_name']}:\nTotal count: {total_workers}\n\nIf you want to change a role or see list worker tasks click on the worker name."
    elif lang == 'ru':
        text = f"Сотрудники {company['company_name']}:\nВсего: {total_workers} сотрудников\n\nЕсли хотите изменить роль или посмотреть задачи сотрудника, нажмите на его имя."
    elif lang == 'uz':
        text = f"{company['company_name']} xodimlari:\nJami: {total_workers} xodim\n\nAgar siz xodimning rolini o'zgartirish yoki vazifalar ro'yxatini ko'rishni xohlaysiz, xodimning ismiga bosing."

    keyboard = []

    for worker in current_workers:
        if worker['user_id'] == user_id:
            if lang == 'ru':
                keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']} - Вы", callback_data=f"settings")])
            elif lang == 'uz':
                keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']} - Siz", callback_data=f"settings")])
            elif lang == 'en':
                keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']} - You", callback_data=f"settings")])
        else:
            keyboard.append([InlineKeyboardButton(text=worker['fullname'], callback_data=f"show_worker_{worker['id']}")])
        


    # Pagination buttons
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=back_page[user['lang']], callback_data=f"list_workers_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page[user['lang']], callback_data=f"list_workers_{page + 1}")])

    # Add the back button at the bottom
    keyboard.append([back_to_company[user['lang']]])

    # Send or edit message
    try:
        await callback.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown'
        )
        await state.update_data(main_menu_message_id=callback.message.message_id)
    except Exception:
        sent_message = await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
        await state.update_data(main_menu_message_id=sent_message.message_id)

