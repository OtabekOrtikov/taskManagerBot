from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_company
from qarz_states import CompanyRegistration
from qarz_utils.btns import back_btn

async def process_company_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("lang")
    company_name = message.text

    if not company_name:
        await message.answer("❗Введите название компании")
        return
    
    await state.update_data({"company_name": company_name})

    company = await get_company(user_id)
    if company is not None:
        await message.answer("❗Вы уже зарегистрированы в системе")
        return
    
    text = {
        "ru": "❗ Введите номер телефона компании в формате +998901234567",
        "uz": "❗ Kompaniya telefon raqamini +998901234567 formatda kiriting",
        "oz": "❗ Компания телефон рақамини +998901234567 форматда киритинг"
    }

    send_text = await message.answer(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))

    await state.update_data({"main_message_id": send_text.message_id})
    await state.set_state(CompanyRegistration.company_phone)