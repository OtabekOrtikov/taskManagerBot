from datetime import datetime
from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_states import GiveDebtCreation
from qarz_utils.parser_date import parse_date
from qarz_utils.basic_texts import end_text, skip_text
from qarz_utils.btns import back_btn

async def handle_due_date_entry(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    data = await state.get_data()
    loan_date = data.get("givedebt_loan_date")

    full_amount = data.get("givedebt_full_amount", 0)  # Ensure amount exists

    # 🟢 **Fixing Split Issue**: If user only enters a date, it will be handled correctly
    parts = message.text.split(" ", 1)
    due_date_str = parts[0]
    amount = int(parts[1]) if len(parts) > 1 else int(full_amount)  # Ensure int conversion

    try:
        due_date = datetime.strptime(parse_date(due_date_str, lang, datetime.strptime(loan_date, "%d.%m.%Y")), "%d.%m.%Y")
    except ValueError as e:
        await message.answer(str(e))
        return

    due_dates = data.get("givedebt_due_date", [])
    amounts = data.get("givedebt_amounts", [])

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

    await state.update_data({"givedebt_due_date": due_dates, "givedebt_amounts": amounts})

    # 🟢 **Fixing Transition Issue**: Skip the "add another date?" question if user enters only a date
    if len(parts) == 1:
        next_step_text = {
            "ru": "✅ Дата возврата долга сохранена. Переход к следующему шагу.\n💬Хотите добавить комментарий к долгу?",
            "uz": "✅ Qarz qaytarish sanasi saqlandi. Keyingi bosqichga o'tildi.\n💬Qarzga izoh qo'shmoqchimisiz?",
            "oz": "✅ Қарз қайтариш санаси сақланди. Кейинги босқичга ўтилди.\n💬Қарзга изоҳ қўшишни хоҳлайсизми?"
        }

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=skip_text[lang], callback_data="givedebt_skip_comment")],
            [back_btn[lang]]
        ])

        send_message = await message.answer(next_step_text[lang], reply_markup=keyboard)
        await state.update_data({"main_message_id": send_message.message_id})
        await state.set_state(GiveDebtCreation.givedebt_comment)
        return  # ✅ **Fixed: Now it will stop execution here and move forward**

    # 🟢 Otherwise, ask if they want to add another date
    add_more_text = {
        "ru": "☑️Хотите добавить ещё дату или завершить?",
        "uz": "☑️Yana sanani qo'shishni xohlaysizmi yoki yakunlaysizmi?",
        "oz": "☑️Яна санани қўшишни хоҳлайсизми ёки якунлайсизми?"
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=end_text[lang], callback_data="givedebt_finish_due")]
    ])

    send_message = await message.answer(add_more_text[lang], reply_markup=keyboard)
    await state.update_data({"main_message_id": send_message.message_id})
    await state.set_state(GiveDebtCreation.givedebt_due_date)
