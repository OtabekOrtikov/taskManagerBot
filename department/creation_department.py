from aiogram.fsm.context import FSMContext
from database.db_utils import get_db_pool, get_user
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from btns import back_to_company
from states import DepartmentCreation

async def creation_department(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id != callback.message.message_id:
        await callback.answer(f"This button is no longer active.")
        return

    db = await get_db_pool()
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    async with db.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])

    text = {
        'en': f"Enter the name of the new department for your company “{company['company_name']}”.",
        'ru': f"Введите название нового отдела для вашей компании “{company['company_name']}”.",
        'uz': f"Kompaniyangiz “{company['company_name']}” uchun yangi bo'lim nomini kiriting."
    }

    keyboard = [[back_to_company[lang]]]

    await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.set_state(DepartmentCreation.department_name)
    await state.update_data(main_menu_message_id=callback.message.message_id)