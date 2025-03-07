import json
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_db_pool, get_user
from qarz_config import BOT_USERNAME, PAGE_SIZE
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import creation_givedebt_text, next_page_text, noactive_btn

async def skip_comment_givedebt(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    data = await state.get_data()

    main_message_id = data.get("main_message_id")
    if main_message_id != callback.message.message_id:
        await callback.answer(noactive_btn[lang])
        return

    creditor_name = data.get("givedebt_debtor")
    creditor_phone_number = data.get("givedebt_debtor_phone")
    amount = int(data.get("givedebt_amount"))
    currency = data.get("givedebt_currency")
    loan_date = datetime.strptime(data.get("givedebt_loan_date"), "%d.%m.%Y")
    due_dates = [
        datetime.strptime(item["due_date"], "%d.%m.%Y").strftime("%d.%m.%Y")
        for item in data.get("givedebt_due_date", [])
    ]
    divided_amounts = [
        int(item["divided_amount"])
        for item in data.get("givedebt_amounts", [])
    ]

    # Serialize due_dates to JSON
    due_dates_json = json.dumps(due_dates)
    amounts_json = json.dumps(divided_amounts)  

    text = creation_givedebt_text(user, data)

    db = await get_db_pool()
    async with db.acquire() as connection:
        new_debt_id = await connection.fetchval("""
            INSERT INTO debts (draft_name, draft_phone, debtor_id, full_amount, currency, loan_date, due_date, comment, status, amounts)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10::jsonb)
            RETURNING id;
        """, creditor_name, creditor_phone_number, user['id'], amount, currency, loan_date, due_dates_json, '', "draft", amounts_json)

        users = await connection.fetch("""
            SELECT DISTINCT u.id, u.fullname 
            FROM debts d 
            INNER JOIN users u 
                ON (d.debtor_id = u.id OR borrower_id = u.id) AND u.id != $1 
            WHERE d.debtor_id = $1 OR d.borrower_id = $1
        """, user['id'])

    referal_text = {
        "ru": "Вы спросили от меня долг, подтвердите это пожалуйста.",
        "oz": "Сиз мендан қарз сўрадингиз, илтимос, тасдиқланг.",
        "uz": "Siz mendan qarz so'radingiz, iltimos tasdiqlang."
    }

    referal_link = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=givedebt_{new_debt_id}&text={referal_text[lang]}"

    keyboard_text = {
        "ru": "↗️Отправить реферальную ссылку",
        "uz": "↗️Referal havolani yuborish",
        "oz": "↗️Реферал ҳаволани юбориш"
    }

    keyboard = [
        [InlineKeyboardButton(text=keyboard_text[lang], url=referal_link)],
        *[
            [InlineKeyboardButton(text=useri['fullname'], callback_data=f"givedebt_{useri['id']}_{new_debt_id}")]
            for useri in users[:PAGE_SIZE]
        ],
        [back_btn[lang]]
    ]

    if len(users) > PAGE_SIZE:
        keyboard.append([InlineKeyboardButton(text=next_page_text, callback_data=f"givedebt_userlist_{new_debt_id}_2")])

    send_text = await callback.message.edit_text(
        text[lang],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.update_data({"main_message_id": send_text.message_id})
