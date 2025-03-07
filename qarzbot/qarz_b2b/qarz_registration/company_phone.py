import re
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from qarz_database.db_utils import get_user, get_company, get_db_pool
from qarz_states import CompanyRegistration
from qarz_utils.btns import back_btn

async def process_company_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']
    data = await state.get_data()
    company_name = data.get("company_name")
    phone_number = message.text

    normalized_phone_number = phone_number.lstrip('+')

    db_pool = get_db_pool()

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        if phone_number.startswith('+'):
            phone_number = phone_number
        else:
            phone_number = f'+{phone_number}'
        async with db_pool.acquire() as connection:
            await connection.execute("INSERT INTO company (company_name, company_phone, responsible_id) VALUES ($1, $2, $3)", company_name, phone_number, user['id'])

        text = {
            "ru": "✅ Отлично, мы создали компанию и привязали вас как ответственного. Теперь вы можете дальше работать с компанией.",
            "uz": "✅ Ajoyib, biz kompaniyani yaratdik va sizni mas'ul shaxs sifatida bog'ladik. Endi siz kompaniya bilan ishlashni davom ettirishingiz mumkin.",
            "oz": "✅ Ажойиб, биз компанияни яратдик ва сизни масъул шахс сифатида бўладик. Энди сиз компания билан ишлашни давом эттиришингиз мумкин."
        }

        await message.answer(text=text[lang])
        company_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Продажа в долг", callback_data="create_lending")],
            [InlineKeyboardButton(text="➕ Получить товара в долг", callback_data="get_lending")],
            [InlineKeyboardButton(text="📊 Мои долги", callback_data="view_lending"),
            InlineKeyboardButton(text="📜 История транзакций", callback_data="transaction_history")],
            [InlineKeyboardButton(text="⚙️ Настройки" , callback_data="b_settings")],
        ])

        await message.answer("🏢 Меню компании", reply_markup=company_menu_keyboard)
    else:
        text = {
            "ru": "❗ Номер телефона введен неверно. Пожалуйста, введите номер в формате +998XXXXXXXXX",
            "uz": "❗ Telefon raqami noto'g'ri kiritildi. Iltimos, telefon raqamini +998XXXXXXXXX formatda kiriting",
            "oz": "❗ Телефон рақами нотўғри киритилди. Илтимос, телефон рақамини +998XXXXXXXXX форматда киритинг"
        }
        await message.answer(text=text[lang])
        return