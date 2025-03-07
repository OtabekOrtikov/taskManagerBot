from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user_lang
from qarz_utils.parser_date import parse_date


async def handle_due_date_entry(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    data = await state.get_data()
    loan_date = data.get("getdebt_loan_date")

    full_amount = data.get("getdebt_full_amount", 0)

    parts = message.text.split(" ", 1)
    due_date_str = parts[0]
    amount = int(parts[1]) if len(parts) > 1 else int(full_amount or 0)

    try:
        due_date = datetime.strptime(parse_date(due_date_str, lang, datetime.strptime(loan_date, "%d.%m.%Y")), "%d.%m.%Y")
    except ValueError as e:
        await message.answer(str(e))
        return

    due_dates = data.get("getdebt_due_date", [])
    amounts = data.get("getdebt_amounts", [])

    if due_dates:
        last_due_date = datetime.strptime(due_dates[-1]["due_date"], "%d.%m.%Y")
        if due_date <= last_due_date:
            error_text = {
                "ru": "❗Дата возврата должна быть позже предыдущей.",
                "uz": "❗Qaytarish sanasi oldingi sanadan keyin bo'lishi kerak.",
                "oz": "❗Қайтариш санаси олдинги санадан кейин бўлиши керак."
            }
            await message.answer(error_text[lang])
            return

    due_dates.append({"due_date": due_date.strftime("%d.%m.%Y")})
    amounts.append({"divided_amount": amount})

    await state.update_data({"getdebt_due_date": due_dates, "getdebt_amounts": amounts})
