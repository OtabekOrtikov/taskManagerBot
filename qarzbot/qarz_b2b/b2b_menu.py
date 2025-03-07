from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_company
from qarz_states import CompanyRegistration
from qarz_utils.btns import back_btn

async def b2b_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_type = data.get("user_type")
    user = await get_user(callback.from_user.id)
    lang = user.get("lang")

    if (user_type == "user"):
        await state.update_data("user_type", "business")
    
    company = await get_company(callback.from_user.id)

    none_company_text = {
        "ru": "❗Вы не являетесь представителем компании. Пожалуйста, зарегистрируйте компанию.\n\nКак называется ваша компания?",
        "uz": "❗Siz kompaniya vakili emassiz. Iltimos, kompaniyani ro'yxatdan o'tkazing.\n\nSizning kompaniyangizning nomi nima?",
        "oz": "❗Сиз компания вакили эмассиз. Илтимос, компанияни рўйхатдан ўтказинг.\n\nСизнинг компаниянгизнинг номи нима?"
    }

    if company is None:
        await callback.message.edit_text(none_company_text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
        await state.set_state(CompanyRegistration.company_name)
        return
    
    company_menu_text = {
        "ru": "🏢 **Меню компании**",
        "uz": "🏢 **Kompaniya menyusi**",
        "oz": "🏢 **Компания менюси**"
    }

    company_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Продажа в долг", callback_data="create_lending")],
        [InlineKeyboardButton(text="➕ Получить товара в долг", callback_data="get_lending")],
        [InlineKeyboardButton(text="📊 Мои долги", callback_data="view_lending"),
         InlineKeyboardButton(text="📜 История транзакций", callback_data="transaction_history")],
        [InlineKeyboardButton(text="⚙️ Настройки" , callback_data="b_settings")],
    ])

    await callback.message.edit_text(company_menu_text[lang], reply_markup=company_menu_keyboard)