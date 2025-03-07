from datetime import datetime
from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_states import GiveDebtCreation
from qarz_utils.basic_texts import skip_text, noactive_btn
from qarz_utils.btns import back_btn

async def givedebt_stop_due_date(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    data = await state.get_data()

    message_id = data.get("main_message_id")
    if callback.message.message_id != message_id:
        await callback.answer(noactive_btn[lang])
        return

    due_date = data.get("givedebt_due_date", [])
    amounts = data.get("givedebt_amounts", [])
    currency = data.get("givedebt_currency")

    # Ensure `due_date` is a list
    if not due_date:
        await callback.answer("❌ No due dates found.")
        return

    # Prepare text message
    text = {
        "ru": f"✅ Даты возврата долга:\n",
        "uz": f"✅ Qarz qaytarish sanalari:\n",
        "oz": f"✅ Қарз қайтариш саналари:\n"
    }

    for i, (due, amount) in enumerate(zip(due_date, amounts)):
        text[lang] += f"{i+1}. {due['due_date']} - {amount} {currency}\n"

    text['ru'] += f"\n💬Хотите добавить комментарий к долгу?"
    text['uz'] += f"\n💬Qarzga izoh qo'shmoqchimisiz?"
    text['oz'] += f"\n💬Қарзга изоҳ қўшишни хоҳлайсизми?"

    # Inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_text[lang], callback_data="givedebt_skip_comment")],
        [back_btn[lang]]
    ])

    # Send updated message
    send_message = await callback.message.edit_text(text[lang], reply_markup=keyboard)
    await state.update_data({"main_message_id": send_message.message_id})
    await state.set_state(GiveDebtCreation.givedebt_comment)
