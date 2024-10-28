from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, back_page, next_page

from config import BOT_USERNAME, PAGE_SIZE

async def list_department_workers(callback: types.CallbackQuery, state: FSMContext):
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
    department_id = int(data[2])
    page = int(data[-1]) if len(data) > 3 else 1

    async with db_pool.acquire() as connection:
        # Fetch all workers for pagination
        workers = await connection.fetch("SELECT * FROM users WHERE company_id = $1 AND department_id = $2", user['company_id'], department_id)
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        department = await connection.fetchrow("SELECT * FROM department WHERE id = $1", department_id)

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
    text = f"Список сотрудников отдела ‘{department['department_name']}’ компании ‘**{company['company_name']}**’:" if user['lang'] == 'ru' else f"‘**{company['company_name']}**’ kompaniyasining xodimlari ro‘yxati:"
    keyboard = []

    referal_link = f"https://t.me/{BOT_USERNAME}?start={company['id']}_group={department_id}"

    # Worker buttons
    if total_workers > 0:
        for worker in current_workers:
            keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']}{" - Вы" if worker['user_id'] == user_id and user['lang'] == 'ru' else " - Bu siz"}", callback_data=f"show_worker_{worker['id']}")])
    else:
        if lang == 'ru':
            share_link = f"https://t.me/share/url?url={referal_link}&text=Ребята, нажмите, пожалуйста, на ссылку, чтобы получить задачу от начальства."
            text = f"В отделе '{department['department_name']}' нет сотрудников."
            keyboard.append([InlineKeyboardButton(text="Добавить сотрудника", url=share_link)])
        elif lang == 'uz':
            share_link = f"https://t.me/share/url?url={referal_link}&text=Yigitlar, boshliqdan vazifa olish uchun quyidagi havolaga kiring."
            text = f"'{department['department_name']}' bo‘limida xodimlar yo‘q."
            keyboard.append([InlineKeyboardButton(text="Xodim qo‘shish", url=share_link)])
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

