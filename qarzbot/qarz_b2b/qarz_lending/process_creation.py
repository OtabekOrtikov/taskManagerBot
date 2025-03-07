from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_company
from qarz_utils.btns import back_btn
from qarz_states import LendingState

async def process_lending_creation(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    lang = user['lang']

    company = await get_company(message.from_user.id)

    if company is None:
        text = {
            "ru": "❗ Вы не являетесь представителем компании. Пожалуйста, зарегистрируйте компанию.",
            "uz": "❗ Siz kompaniya vakili emassiz. Iltimos, kompaniyani ro'yxatdan o'tkazing.",
            "oz": "❗ Сиз компания вакили эмассиз. Илтимос, компанияни рўйхатдан ўтказинг."
        }

        await message.answer(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
        return
    
    data = message.text
    splitted_data = data.split(" - ")
    
    if splitted_data[1].isdigit():
        item_name = splitted_data[0]
        quantity = splitted_data[1]
        await state.update_data({"clending_item_name": item_name, "clending_item_measure": quantity})
        await message.reply("✅ Товар и его количество сохранены. Если ещё хотите добавить товар, то введите его название и количество в формате \"Товар - количество\"")