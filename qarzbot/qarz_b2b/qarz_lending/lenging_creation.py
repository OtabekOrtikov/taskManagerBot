from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_company
from qarz_utils.btns import back_btn
from qarz_states import LendingState

async def lending_creation(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    company = await get_company(callback.from_user.id)

    if company is None:
        text = {
            "ru": "❗ Вы не являетесь представителем компании. Пожалуйста, зарегистрируйте компанию.",
            "uz": "❗ Siz kompaniya vakili emassiz. Iltimos, kompaniyani ro'yxatdan o'tkazing.",
            "oz": "❗ Сиз компания вакили эмассиз. Илтимос, компанияни рўйхатдан ўтказинг."
        }

        await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
        return

    text = {
        "ru": "🔥 Отлично.\n\nТеперь если хотите укажите общую сумму или можете указать \"Товар - количество товара\"",
        "uz": "🔥 Juda yaxshi.\n\nEndi xohlasangiz butun summani kiritishingiz mumkin yoki \"Tovar - uning soni\" orqali tovar qo'shishingiz mumkin.",
        "oz": "🔥 Жуда яхши.\n\nЭнди хохласангиз бутун суммани киритишингиз мумкин ёки \"Товар - унинг сони\" орқали товар қўшишингиз мумкин."
    }

    await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
    await state.set_state(LendingState.lending_creation)