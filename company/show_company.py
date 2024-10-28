from aiogram import types
from aiogram.fsm.context import FSMContext

from btns import company_menu_btns
from database.db_utils import *

async def show_company(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    # Check if the callback is from the latest message with the button
    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)

    # Check if user exists
    if user is None:
        await callback.message.answer("User not found. Please register again with /start.")
        return

    lang = user['lang']
    
    async with db_pool.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        count_worker = await connection.fetchval("SELECT COUNT(*) FROM users WHERE company_id = $1", user['company_id'])

    if lang == 'ru':
        await callback.message.edit_text(
            f"**Ваша компания:** ‘{company['company_name']}’ \n**Количество сотрудников:** {count_worker}\nХотите посмотреть другие данные вашей компании?\nНажмите на кнопку чтобы продолжить",
            reply_markup=company_menu_btns['ru'], parse_mode='Markdown'
        )
    elif lang == 'uz':
        await callback.message.edit_text(
            f"**Sizning kompaniyangiz:** ‘{company['company_name']}’ \n**Xodimlar soni:** {count_worker}\nSizning kompaniyangizning boshqa ma'lumotlarini ko'rishni xohlaysizmi?\nDavom etish uchun tugmani bosing",
            reply_markup=company_menu_btns['uz'], parse_mode='Markdown'
        )

    await state.update_data(main_menu_message_id=callback.message.message_id)

