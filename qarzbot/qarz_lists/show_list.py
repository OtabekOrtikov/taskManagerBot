from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user, get_db_pool, get_user_by_id
from qarz_utils.basic_texts import noactive_btn, debt_404, back_text, previous_page_text, next_page_text, currency_parse
from qarz_config import PAGE_SIZE
from qarz_utils.parser_status import parse_status

async def show_list(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']


    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    data = callback.data.split("_")
    list_type = data[1]
    if len(data) > 3:
        other_id = int(data[-2])
        page = int(data[-1])
    else:
        other_id = int(data[-1])
        page = 1

    otheruser = await get_user_by_id(other_id)

    db_pool = await get_db_pool()

    async with db_pool.acquire() as connection:
        if list_type == 'given':
            debts = await connection.fetch("SELECT * FROM debts WHERE debtor_id = $1 AND borrower_id = $2", user['id'], otheruser['id'])
        else:
            debts = await connection.fetch("SELECT * FROM debts WHERE debtor_id = $1 AND borrower_id = $2", otheruser['id'], user['id'])

    total_debts = len(debts)
    total_pages = (total_debts + PAGE_SIZE - 1) // PAGE_SIZE

    if page > total_pages:
        page = total_pages
    if page < 0:
        page = 1

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    current_debts = debts[start:end]

    keyboard = []

    if total_debts == 0:
        keyboard.append([InlineKeyboardButton(text=debt_404[lang], callback_data="no_debt")])
    else:
        for debt in current_debts:
            status = parse_status(debt['status'])[lang]['short']
            keyboard.append([InlineKeyboardButton(text=f"{status} {debt['full_amount']}{currency_parse[debt['currency']]['symbol']} - {debt['loan_date']}", callback_data=f"debt_{debt['id']}")])
    
    if page > 1 and page < total_pages:
        keyboard.append([InlineKeyboardButton(text=previous_page_text[lang], callback_data=f"show_{list_type}_{other_id}_{page - 1}"),
                         InlineKeyboardButton(text=next_page_text[lang], callback_data=f"show_{list_type}_{other_id}_{page + 1}")])
    if page > 1:
        keyboard.append([
            InlineKeyboardButton(text=previous_page_text[lang], callback_data=f"show_{list_type}_{other_id}_{page - 1}")
        ])
    if page < total_pages:
        keyboard.append([
            InlineKeyboardButton(text=next_page_text[lang], callback_data=f"show_{list_type}_{other_id}_{page + 1}")
        ])

    keyboard.append([InlineKeyboardButton(text=back_text[lang], callback_data=f"user_{other_id}")])

    text = {
        "given": {
            "ru": f"📑 Список долгов которые Вы дали {otheruser['fullname']}:",
            "uz": f"📑 {otheruser['fullname']}ga bergan qarzlar ro'yhati:",
            "oz": f"📑 {otheruser['fullname']}га берган қарзлар рўйҳати"
        },
        "taken": {
            "ru": f"📑 Список долгов которые Вы взяли у {otheruser['fullname']}:",
            "uz": f"📑 {otheruser['fullname']}dan olingan qarzlar ro'yhati:",
            "oz": f"📑 {otheruser['fullname']}дан олинган қарзлар рўйҳати"
        }
    }

    send_message = await callback.message.edit_text(text[list_type][lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({ "main_message_id": send_message.message_id })