from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user, get_db_pool
from btns import back_to_company, back_page, next_page

router = Router()

# Max items per page
ITEMS_PER_PAGE = 5

async def list_workers(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.", show_alert=True)
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
    total_pages = (total_workers + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # Adjust the page if out of bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Paginate workers
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_workers = workers[start:end]

    # Build message text and keyboard
    text = f"Список сотрудников компании ‘**{company['company_name']}**’:" if user['lang'] == 'ru' else f"‘**{company['company_name']}**’ kompaniyasining xodimlari ro‘yxati:"
    keyboard = []

    # Worker buttons
    for worker in current_workers:
        keyboard.append([InlineKeyboardButton(text=f"{worker['fullname']}{" - Вы" if worker['user_id'] == user_id and user['lang'] == 'ru' else " - Bu siz"}", callback_data=f"show_worker_{worker['id']}")])

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

