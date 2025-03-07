from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_states import GetDebtCreation
from qarz_utils.parser_date import parse_date
from qarz_utils.btns import divide_btn

async def process_loan_date_getdebt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    try:
        loan_date = parse_date(message.text, lang)
    except ValueError as e:
        await message.answer(str(e))
        return

    await state.update_data({
        "getdebt_loan_date": loan_date,
        "getdebt_due_date": []
    })

    text = {
        "ru": "📅 Пожалуйста, укажите дату возврата долга. Выберите способ разделения или укажите дату вручную в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.",
        "uz": "📅 Iltimos, qarzni qaytarish sanasini kiriting. Bo'lib bo'lmaganini tanlang yoki qo'lda kiriting. Формат: КК.ОО.ЙЙЙЙ yoki КК.ОО.ЙЙ.",
        "oz": "📅 Илтимос, қарзни қайтариш санасини киритинг. Бўлиб бўлмаганини танланг ёки қўлда киритинг. Формат: КК.ОО.ЙЙЙЙ ёки КК.ОО.ЙЙ."
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=divide_btn[lang])

    await message.answer(text[lang], reply_markup=keyboard)
    await state.set_state(GetDebtCreation.getdebt_due_date)
