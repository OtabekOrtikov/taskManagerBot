import json
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from qarz_database.db_utils import get_user, get_db_pool
from qarz_lists.given_debts import given_list  # Given debts list (if exists)
from qarz_lists.taken_debts import get_list  # Get debts list (if exists)
from qarz_utils.btns import filter_settings_btn, filter_date_btn, filter_currency_btn, filter_status_btn

text = {
    "ru": "Настройки фильтра",
    "uz": "Filtr sozlamalari",
    "oz": "Фильтр созламалари"
}

async def load_user_filter_settings(db, user_id: int) -> dict:
    """Load filter_settings JSON from DB, return as dict."""
    existing_json = await db.fetchval("SELECT filter_settings FROM users WHERE user_id = $1", user_id)
    return json.loads(existing_json) if existing_json else {}

async def save_user_filter_settings(db, user_id: int, filter_settings: dict):
    """Save the given filter_settings dict to the DB (json-encoded)."""
    await db.execute("UPDATE users SET filter_settings = $1 WHERE user_id = $2",
                     json.dumps(filter_settings), user_id)

async def filter_settings(callback: types.CallbackQuery, state: FSMContext):
    """ Show the main filter settings menu & track which debts list the user came from. """
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    data = callback.data.split("_")
    prev_list = data[1] if len(data) > 1 else "given_debts"  # Default to given_debts
    await state.update_data(previous_list=prev_list)

    keyboard = InlineKeyboardMarkup(inline_keyboard=filter_settings_btn[lang])

    send_message = await callback.message.edit_text(
        "🔍 " + text[lang],
        reply_markup=keyboard
    )
    await state.update_data({"main_message_id": send_message.message_id})

async def filter_generic_process(callback: types.CallbackQuery, state: FSMContext, filter_type: str):
    """ Remove all filters and set only the selected filter. """
    user_id = callback.from_user.id
    db_pool = await get_db_pool()
    
    async with db_pool.acquire() as db:
        # Reset filter settings (remove all previous filters)
        filter_settings = {filter_type: callback.data.split("_")[-1]}

        # Update the database with only the selected filter
        await db.execute(
            "UPDATE users SET filter_settings = $1 WHERE user_id = $2",
            json.dumps(filter_settings), user_id
        )

    state_data = await state.get_data()
    prev_list = state_data.get("previous_list", "given_debts")

    # Get the current page from state (default to 1 if not found)
    current_page = state_data.get("current_page", 1)

    # Redirect the user back to the correct list with page number
    if prev_list == "given_debts":
        await given_list(callback, state, page=current_page)
    elif prev_list == "get_debts":
        await get_list(callback, state, page=current_page)
    else:
        await given_list(callback, state, page=current_page)  # Default

# 📌 Date Filter Menu
async def filter_date(callback: types.CallbackQuery, state: FSMContext):
    """ Show the date filter selection menu """
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    keyboard = InlineKeyboardMarkup(inline_keyboard=filter_date_btn[lang])

    send_message = await callback.message.edit_text(
        text[lang], reply_markup=keyboard
    )
    await state.update_data({"main_message_id": send_message.message_id})

# 📌 Currency Filter Menu
async def filter_currency(callback: types.CallbackQuery, state: FSMContext):
    """ Show the currency filter selection menu """
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    keyboard = InlineKeyboardMarkup(inline_keyboard=filter_currency_btn[lang])

    send_message = await callback.message.edit_text(
        text[lang], reply_markup=keyboard
    )
    await state.update_data({"main_message_id": send_message.message_id})

# 📌 Status Filter Menu
async def filter_status(callback: types.CallbackQuery, state: FSMContext):
    """ Show the status filter selection menu """
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    keyboard = InlineKeyboardMarkup(inline_keyboard=filter_status_btn[lang])

    send_message = await callback.message.edit_text(
        text[lang], reply_markup=keyboard
    )
    await state.update_data({"main_message_id": send_message.message_id})

# 📌 Process Filter Changes
async def filter_date_process(callback: types.CallbackQuery, state: FSMContext):
    await filter_generic_process(callback, state, "filter_date")

async def filter_currency_process(callback: types.CallbackQuery, state: FSMContext):
    await filter_generic_process(callback, state, "filter_currency")

async def filter_status_process(callback: types.CallbackQuery, state: FSMContext):
    await filter_generic_process(callback, state, "filter_status")
