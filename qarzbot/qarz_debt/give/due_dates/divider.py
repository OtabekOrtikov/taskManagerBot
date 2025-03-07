from datetime import datetime
from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dateutil.relativedelta import relativedelta

from qarz_states import GiveDebtCreation
from qarz_utils.basic_texts import skip_text
from qarz_utils.btns import back_btn

async def handle_division_choice(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    division = callback.data.split("_")[-1]

    loan_date = datetime.strptime((await state.get_data()).get("givedebt_loan_date"), "%d.%m.%Y")
    total_amount = int((await state.get_data()).get("givedebt_amount"))
    if not loan_date or not total_amount:
        await callback.answer("Ошибка: отсутствуют данные о сумме или дате займа.")
        return

    division = int(division)
    due_dates = [(loan_date + relativedelta(months=i)).strftime("%d.%m.%Y") for i in range(1, division + 1)]

    base_amount = total_amount // division
    remainder = total_amount % division

    divided_amounts = [base_amount] * division
    for i in range(remainder):
        divided_amounts[i] += 1

    due_dates_json = [{"due_date": date} for date in due_dates]
    divided_amounts_json = [{"divided_amount": amount} for amount in divided_amounts]

    await state.update_data({"givedebt_due_date": due_dates_json, "givedebt_amounts": divided_amounts_json})

    text = {
        "ru": f"✅ Сумма долга разделена на {division} частей:\n",
        "uz": f"✅ Qarz summasi {division} qismga bo'lingan:\n",
        "oz": f"✅ Қарз суммаси {division} қисмга бўлинган:\n"
    }

    currency = (await state.get_data()).get("givedebt_currency")

    for i, (due, amount) in enumerate(zip(due_dates, divided_amounts)):
        text[lang] += f"{i+1}. {due} - {amount} {currency}\n"

    text['ru'] += f"\n💬Введите комментарий к долгу или можете продолжить без него."
    text['uz'] += f"\n💬Qarzga izoh qoldiring yoki tashqi izohsiz davom etishingiz mumkin."
    text['oz'] += f"\n💬Қарзга изоҳ қўйинг ёки ташқи изоҳсиз давом этингиз мумкин."

    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_text[lang], callback_data="givedebt_skip_comment")],
        [back_btn[lang]]
    ]))
    await state.update_data({"main_message_id": send_message.message_id})
    await state.set_state(GiveDebtCreation.givedebt_comment)
