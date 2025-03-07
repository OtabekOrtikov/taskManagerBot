from datetime import datetime
import json
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_db_pool, get_user
from qarz_config import BOT_USERNAME, PAGE_SIZE
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import creation_getdebt_text, next_page_text, noactive_btn, previous_page_text

async def getdebt_userlist(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    data = await state.get_data()

    main_message_id = data.get("main_message_id")
    if main_message_id != callback.message.message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    page = int(callback.data.split("_")[-1])

    creditor_name = data.get("getdebt_creditor")
    creditor_phone_number = data.get("getdebt_creditor_phone")
    amount = int(data.get("getdebt_amount"))
    currency = data.get("getdebt_currency")
    loan_date = datetime.strptime(data.get("getdebt_loan_date"), "%d.%m.%Y")
    due_dates = [
        datetime.strptime(item["due_date"], "%d.%m.%Y").strftime("%d.%m.%Y")
        for item in data.get("getdebt_due_date", [])
    ]
    divided_amounts = [
        int(item["divided_amount"])
        for item in data.get("getdebt_amounts", [])
    ]
    comment = data.get("getdebt_comment", "")

    # Serialize due_dates to JSON
    due_dates_json = json.dumps(due_dates)
    amounts_json = json.dumps(divided_amounts)

    text = creation_getdebt_text(user, data, comment)

    db = await get_db_pool()
    async with db.acquire() as connection:
        new_debt_id = await connection.fetchval("""
            INSERT INTO debts (draft_name, draft_phone, borrower_id, full_amount, currency, loan_date, due_date, comment, status, amounts)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10::jsonb)
            RETURNING id;
        """, creditor_name, creditor_phone_number, user['id'], amount, currency, loan_date, due_dates_json, comment, "draft", amounts_json)

        users = await connection.fetch("""
            SELECT DISTINCT u.id, u.fullname 
            FROM debts d 
            INNER JOIN users u 
                ON (d.debtor_id = u.id OR borrower_id = u.id) AND u.id != $1 
            WHERE d.debtor_id = $1 OR d.borrower_id = $1
        """, user['id'])

    referal_text = {
        "ru": "Я хочу взять долг, можете подтвердить?",
        "uz": "Qarz olmoqchiman, tasdiqlay olasizmi?",
        "oz": "Қарз олмоқчиман, тасдиқлай оласизми?"
    }

    referal_link = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=getdebt_{new_debt_id}&text={referal_text[lang]}"

    keyboard_text = {
        "ru": "↗️Отправить реферальную ссылку",
        "uz": "↗️Referal havolani yuborish",
        "oz": "↗️Реферал ҳаволани юбориш"
    }

    total_page = len(users) // PAGE_SIZE
    if len(users) % PAGE_SIZE:
        total_page += 1
    
    if page > total_page:
        page = total_page
    elif page < 2:
        page = 2

    users = users[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]

    keyboard = [
        [InlineKeyboardButton(text=keyboard_text[lang], url=referal_link)],
        *[
            [InlineKeyboardButton(text=useri['fullname'], callback_data=f"getdebt_{useri['id']}_{new_debt_id}")]
            for useri in users
        ],
        [back_btn[lang]]
    ]

    if page > 1:
        keyboard.append([InlineKeyboardButton(text=previous_page_text[lang], callback_data=f"getdebt_userlist_{new_debt_id}_{page - 1}")])
    if page < total_page:
        keyboard.append([InlineKeyboardButton(text=next_page_text[lang], callback_data=f"getdebt_userlist_{new_debt_id}_{page + 1}")])    
    send_text = await callback.message.edit_text(
        text[lang],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.update_data({"main_message_id": send_text.message_id})
