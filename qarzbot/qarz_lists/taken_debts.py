import json
import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from qarz_database.db_utils import get_user, get_db_pool
from qarz_config import PAGE_SIZE
from qarz_utils.basic_texts import noactive_btn, previous_page_text, next_page_text, debt_404, currency_parse
from qarz_utils.btns import filter_btn, back_btn
from qarz_utils.parser_status import parse_status

def convert_to_uzs(amount: float, currency: str) -> float:
    """Convert the given amount to UZS for consistent sorting."""
    rates = {'usd': 13000, 'eur': 14000, 'rub': 133, 'uzs': 1}
    return amount * rates.get(currency.lower(), 1)

STATUS_PRIORITY_MAP = {
    'overdue': ['overdue', 'active', 'completed', 'draft'],
    'active': ['active', 'overdue', 'completed', 'draft'],
    'completed': ['completed', 'active', 'overdue', 'draft'],
    'draft': ['draft', 'active', 'overdue', 'completed'],
}

CURRENCY_PRIORITY_MAP = {
    'usd': ['usd', 'uzs', 'eur', 'rub'],
    'uzs': ['uzs', 'usd', 'eur', 'rub'],
    'eur': ['eur', 'usd', 'uzs', 'rub'],
    'rub': ['rub', 'usd', 'uzs', 'eur'],
}

def make_sort_key(debt: dict, filter_settings: dict) -> tuple:
    """Sort debts based on user-defined filters: currency, status, date, and amount."""
    currency = debt['currency'].lower()
    currency_pos = CURRENCY_PRIORITY_MAP.get(filter_settings.get("filter_currency"), []).index(currency) if filter_settings.get("filter_currency") else 0
    status_pos = STATUS_PRIORITY_MAP.get(filter_settings.get("filter_status"), []).index(debt['status']) if filter_settings.get("filter_status") else 0
    date_key = -debt['loan_date'].timestamp() if filter_settings.get("filter_date") == 'new' else debt['loan_date'].timestamp()
    amount_key = -convert_to_uzs(debt['full_amount'], currency) if filter_settings.get("filter_amount") == 'big' else convert_to_uzs(debt['full_amount'], currency)
    return (currency_pos, status_pos, date_key, amount_key)

async def get_list(callback: types.CallbackQuery, state: FSMContext, page: int = 1):
    """ Show the taken debts list, applying filters first, then showing other debts. """
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return

    data = callback.data.split("_")

    # Ensure correct page handling
    if len(data) > 2 and data[-1].isdigit():
        page = int(data[-1])  # Ensure page is an integer

    db_pool = await get_db_pool()
    async with db_pool.acquire() as db:
        # Load saved filter settings
        user_filter = await db.fetchval("SELECT filter_settings FROM users WHERE user_id = $1", user_id)
        filter_settings = json.loads(user_filter) if user_filter else {}

        # Fetch all debts (unfiltered)
        all_debts = await db.fetch("SELECT * FROM debts WHERE borrower_id = $1 ORDER BY loan_date ASC", user['id'])

        # Separate debts into two lists: filtered & others
        filtered_debts = []
        other_debts = []

        for debt in all_debts:
            matches_filter = True

            # Check filters and separate debts
            if "filter_currency" in filter_settings and debt["currency"] != filter_settings["filter_currency"]:
                matches_filter = False
            if "filter_status" in filter_settings and debt["status"] != filter_settings["filter_status"]:
                matches_filter = False

            if matches_filter:
                filtered_debts.append(debt)
            else:
                other_debts.append(debt)

        # Sorting debts
        if "filter_date" in filter_settings and filter_settings["filter_date"] == "new":
            filtered_debts.sort(key=lambda d: d["loan_date"], reverse=True)
            other_debts.sort(key=lambda d: d["loan_date"], reverse=True)
        else:
            filtered_debts.sort(key=lambda d: d["loan_date"])
            other_debts.sort(key=lambda d: d["loan_date"])

        # Final sorted debts list: First show filtered debts, then others
        debts = filtered_debts + other_debts

    total_debts = len(debts)
    total_pages = (total_debts + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(1, min(page, total_pages))  # Ensure page is valid

    # Save the current page in state
    await state.update_data(current_page=page)

    keyboard = [filter_btn[lang]]

    start, end = (page - 1) * PAGE_SIZE, page * PAGE_SIZE
    current_debts = debts[start:end]

    if total_debts == 0:
        keyboard.append([InlineKeyboardButton(text=debt_404[lang], callback_data="no_debt")])
    else:
        for debt in current_debts:
            async with db_pool.acquire() as db:
                debtor = await db.fetchrow("SELECT * FROM users WHERE id = $1", debt['debtor_id'])
            status = parse_status(debt['status'])[lang]['short']
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{debtor['fullname']} - {debt['full_amount']}{currency_parse[debt['currency']]['symbol']} {status}",
                    callback_data=f"debt_{debt['id']}"
                )
            ])

    if page > 1:
        keyboard.append([InlineKeyboardButton(text=previous_page_text[lang], callback_data=f"get_debts_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page_text[lang], callback_data=f"get_debts_{page + 1}")])

    keyboard.append([back_btn[lang]])

    send_message = await callback.message.edit_text(
        f"\U0001F4CB Долги которые Вы взяли:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.update_data({"main_message_id": send_message.message_id})
