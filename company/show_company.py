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
    lang = user['lang']
    
    async with db_pool.acquire() as connection:
        company = await connection.fetchrow("SELECT * FROM company WHERE id = $1", user['company_id'])
        count_worker = await connection.fetchval("SELECT COUNT(*) FROM users WHERE company_id = $1", user['company_id'])

        text = {
            'ru': f"**Ваша компания:** ‘{company['company_name']}’ \n**Количество сотрудников:** {count_worker}\nХотите посмотреть другие данные вашей компании?\nНажмите на кнопку чтобы продолжить",
            'uz': f"**Sizning kompaniyangiz:** ‘{company['company_name']}’ \n**Xodimlar soni:** {count_worker}\nSizning kompaniyangizning boshqa ma'lumotlarini ko'rishni xohlaysizmi?\nDavom etish uchun tugmani bosing",
            'en': f"**Your company:** ‘{company['company_name']}’ \n**Number of employees:** {count_worker}\nDo you want to see other data of your company?\nPress the button to continue"
        }

        if user['role_id'] == 1:
            await callback.message.edit_text(text[lang], reply_markup=company_menu_btns['boss'][lang], parse_mode='Markdown')
        elif user['role_id'] == 2:
            await callback.message.edit_text(text[lang], reply_markup=company_menu_btns['manager'][lang], parse_mode='Markdown')
        else:
            await callback.message.edit_text(text[lang], reply_markup=company_menu_btns['worker'][lang], parse_mode='Markdown')

    await state.update_data(main_menu_message_id=callback.message.message_id)

