from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user_by_id, get_db_pool, get_user
from qarz_utils.basic_texts import noactive_btn, currency_parse

async def show_user(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    data = callback.data.split("_")
    other_id = int(data[-1])
    print(other_id)
    otheruser = await get_user_by_id(other_id)
    print(str(otheruser))
    
    db_pool = await get_db_pool()

    async with db_pool.acquire() as connection:
        taken_debt_amount = await connection.fetch("""
            WITH amount_total AS (
                SELECT COALESCE(SUM(full_amount)::BIGINT, 0) AS total
                FROM debts
                WHERE debtor_id = $1
            ),
            converted_amounts AS (
                SELECT 
                    id,
                    currency, 
                    full_amount,
                    CASE 
                        WHEN currency = 'usd' THEN full_amount * 13000
                        WHEN currency = 'eur' THEN full_amount * 14000
                        WHEN currency = 'rub' THEN full_amount * 133
                        WHEN currency = 'uzs' THEN full_amount
                        ELSE full_amount
                    END AS converted_amount
                FROM debts
                WHERE debtor_id = $1
            ),
            sum_converted_amount AS (
                SELECT COALESCE(SUM(converted_amount)::BIGINT, 0) AS total_converted
                FROM converted_amounts
            )
            SELECT DISTINCT
                amount_total.total,
                sum_converted_amount.total_converted
            FROM debts
            JOIN amount_total ON true
            JOIN sum_converted_amount ON true
            WHERE debtor_id = $1;""", otheruser['id'])

        given_debt_amount = await connection.fetch("""
            WITH amount_total AS (
                SELECT COALESCE(SUM(full_amount)::BIGINT, 0) AS total
                FROM debts
                WHERE debtor_id = $1
            ),
            converted_amounts AS (
                SELECT 
                    id,
                    currency, 
                    full_amount,
                    CASE 
                        WHEN currency = 'usd' THEN full_amount * 13000
                        WHEN currency = 'eur' THEN full_amount * 14000
                        WHEN currency = 'rub' THEN full_amount * 133
                        WHEN currency = 'uzs' THEN full_amount
                        ELSE full_amount
                    END AS converted_amount
                FROM debts
                WHERE debtor_id = $1
            ),
            sum_converted_amount AS (
                SELECT COALESCE(SUM(converted_amount)::BIGINT, 0) AS total_converted
                FROM converted_amounts
            )
            SELECT DISTINCT
                amount_total.total,
                sum_converted_amount.total_converted
            FROM debts
            JOIN amount_total ON true
            JOIN sum_converted_amount ON true
            WHERE debtor_id = $1;""", user['id'])

    # Safely access the first row or provide a default value
    taken_debt_amount = taken_debt_amount[0] if taken_debt_amount else {"total_converted": 0}
    given_debt_amount = given_debt_amount[0] if given_debt_amount else {"total_converted": 0}

    text = {
        "ru": (
            f"📑 Информация о пользователя:\n\n"
            f"👤 ФИО пользователя: {otheruser['fullname']}\n"
            f"📞 Номер телефона: {otheruser['phone_number']}\n"
            f"🥳 Дата рождение: {otheruser['birthdate']}\n\n"

            f"⬇️ Взятые долги: {int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
            f"⬆️ Отданные долги: {int(given_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
            f"📊 Общий баланс: {int(given_debt_amount['total_converted']) - int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
        ),
        "uz": (
            f"📑 Foydalanuvchi haqida ma'lumot:\n\n"
            f"👤 Foydalanuvchi FIO: {otheruser['fullname']}\n"
            f"📞 Telefon raqami: {otheruser['phone_number']}\n"
            f"🥳 Tug'ilgan kun: {otheruser['birthdate']}\n\n"

            f"⬇️ Olingan qarzlar: {int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
            f"⬆️ Berilgan qarzlar: {int(given_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
            f"📊 Umumiy balans: {int(given_debt_amount['total_converted']) - int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\n"
        ),
        "oz": (
            f"📑 Фойдаланувчи ҳақида маълумот:\н\н"
            f"👤 Фойдаланувчи ФИО: {otheruser['fullname']}\н"
            f"📞 Телефон рақами: {otheruser['phone_number']}\н"
            f"🥳 Туғилган кун: {otheruser['birthdate']}\н\н"

            f"⬇️ Олинган қарзлар: {int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\н"
            f"⬆️ Берилган қарзлар: {int(given_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\н"
            f"📊 Умумий баланс: {int(given_debt_amount['total_converted']) - int(taken_debt_amount['total_converted'])} {currency_parse['uzs']['symbol']}\н"
        ),
    }

    keyboard_text = {
        "ru": {
            "given": "⬆️ Отданные долги",
            "taken": "⬇️ Взятые долги",
            "back": "🔙 Назад"
        },
        "uz": {
            "given": "⬆️ Berilgan qarzlar",
            "taken": "⬇️ Olingan qarzlar",
            "back": "🔙 Orqaga"
        },
        "oz": {
            "given": "⬆️ Берилган қарзлар",
            "taken": "⬇️ Олинган қарзлар",
            "back": "🔙 Орқага"
        },
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=keyboard_text[lang]['given'], callback_data=f"show_given_{other_id}")],
        [InlineKeyboardButton(text=keyboard_text[lang]['taken'], callback_data=f"show_taken_{other_id}")],
        [InlineKeyboardButton(text=keyboard_text[lang]['back'], callback_data="people_list")]
    ])

    send_message = await callback.message.edit_text(text=text[lang], reply_markup=keyboard)
    await state.update_data({"main_message_id": send_message.message_id})
