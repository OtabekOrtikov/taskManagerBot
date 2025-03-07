from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from qarz_states import GiveDebtCreation
from qarz_utils.btns import back_btn, currency_btn
from qarz_utils.basic_texts import invalid_amount

async def process_give_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    try:
        # Remove spaces and validate the input
        sanitized_input = message.text.replace(" ", "")
        if sanitized_input.isdigit():
            # Save both formatted and numeric amount
            await state.update_data({
                "givedebt_amount": message.text,
                "givedebt_full_amount": int(sanitized_input)  # Store full amount as integer
            })
        else:
            raise ValueError()
    except ValueError:
        await message.answer(invalid_amount[lang])
        return

    text = {
        "ru": "💰Выберите валюту.",
        "uz": "💰Valyutani tanlang.",
        "oz": "💰Валютани танланг."
    }

    keyboard = []
    for btn in currency_btn['give']:
        keyboard.append(btn)
    keyboard.append([back_btn[lang]])

    send_text = await message.answer(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_text.message_id})
    await state.set_state(GiveDebtCreation.givedebt_currency)
