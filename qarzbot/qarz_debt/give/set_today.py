from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_states import GiveDebtCreation
from qarz_utils.parser_date import parse_date
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import noactive_btn

async def set_today_givedebt(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    loan_date = parse_date("today", lang)

    await state.update_data({
        "givedebt_loan_date": loan_date,
        "givedebt_due_date": []
    })

    text = {
        "ru": "📅 Выберите способ разделения или укажите дату вручную в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.",
        "uz": "📅 Bo'lishini tanlang yoki qo'shimcha sana ko'rsatish uchun KK.OO.YYYY yoki KK.OO.YYYY formatida kiriting.",
        "oz": "📅 Бўлишини танланг ёки қўшимча сана кўрсатиш учун KK.OO.YYYY ёки KK.OO.YYYY форматида киритинг."
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ месяц", callback_data="givedebt_divide_1"),
         InlineKeyboardButton(text="3️⃣ месяца", callback_data="givedebt_divide_3")],
        [InlineKeyboardButton(text="6️⃣ месяцев", callback_data="givedebt_divide_6"),
         InlineKeyboardButton(text="1️⃣2️⃣ месяцев", callback_data="givedebt_divide_12")],
        [back_btn[lang]]
    ])

    await callback.message.edit_text(text[lang], reply_markup=keyboard)
    await state.set_state(GiveDebtCreation.givedebt_due_date)