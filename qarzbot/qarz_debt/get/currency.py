from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from qarz_states import GetDebtCreation
from qarz_utils.btns import back_btn, set_today_btn
from qarz_utils.basic_texts import noactive_btn

async def process_get_currency(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    currency = callback.data.split("_")[-1]
    await state.update_data({"getdebt_currency": currency})
    
    text = {
        "ru": "📅Пожалуйста, укажите дату получения долга в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ. Вы также можете выбрать дату сегодняшнего дня нажав кнопку ниже.",
        "uz": "📅Iltimos, qarz olish sanasini qo'yish uchun KK.OO.YYYY yoki KK.OO.YY formatida kiriting. Siz pasdagi tugmani bosib bugungi kunni tanlashingiz mumkin.",
        "oz": "📅Илтимос, қарз олиш санасини қўйиш учун KK.OO.ЙЙЙЙ ёки KK.OO.ЙЙ форматида киритинг. Сиз пасдаги тугмани босиб бугунги кунни танлашингиз мумкин."
    }
    
    keyboard = []
    keyboard.append([set_today_btn['get'][lang]])
    keyboard.append([back_btn[lang]])
    
    send_text = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_text.message_id})
    await state.set_state(GetDebtCreation.getdebt_loan_date)