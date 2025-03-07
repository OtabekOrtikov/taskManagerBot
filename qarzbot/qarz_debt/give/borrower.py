import re
from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from qarz_states import GiveDebtCreation
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import invalid_phone, invalid_creditor, invalid_d_p_format

async def process_borrower(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    try:
        if len(message.text.split(" - ")) == 2:
            debtor, phone_number = message.text.split(" - ")
            if not re.match(r"^\+998\d{9}$", phone_number):
                raise ValueError(invalid_phone[lang])
            
            if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s-]+$", debtor):
                raise ValueError(invalid_creditor[lang])
            
            await state.update_data({"givedebt_debtor": debtor, "givedebt_debtor_phone": phone_number})
        else:
            raise ValueError(invalid_d_p_format[lang])
        
    except ValueError as e:
        await message.answer(f"{e}")
        return

    text = {
        "ru": "❗Введите сумму долга",
        "oz": "❗Qarz summasini kiriting",
        "uz": "❗Қарз суммасини киритинг"
    }
    send_text = await message.answer(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
    await state.update_data({"main_message_id": send_text.message_id})
    await state.set_state(GiveDebtCreation.givedebt_amount)