from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from qarz_database.db_utils import get_user, get_db_pool

from qarz_utils.basic_texts import previous_page_text, next_page_text, noactive_btn
from qarz_utils.btns import back_btn

async def show_people(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    
    data = callback.data.split("_")
    page = int(data[-1]) if len(data) > 2 else 1
    
    async with db_pool.acquire() as connection:
        users = await connection.fetch("""SELECT DISTINCT u.id, u.fullname 
            FROM debts d 
            INNER JOIN users u 
                ON (d.debtor_id = u.id OR borrower_id = u.id) AND u.id != $1 
            WHERE (d.debtor_id = $1 OR d.borrower_id = $1) AND d.status != 'draft'""", user['id'])
    
    total_users = len(users)
    total_pages = (total_users + 5 - 1) // 5

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * 5
    end = start + 5
    current_users = users[start:end]

    text = {
        "ru": "📑 Список людей которые Вы имеете связь.",
        "uz": "📑 Sizga bog'liq odamlar ro'yxati.",
        "oz": "📑 Сизга боғлиқ одамлар  рўйхати."
    }

    keyboard = []

    for useri in current_users:
        keyboard.append([InlineKeyboardButton(text=f"{useri['fullname']}", callback_data=f"user_{useri['id']}")])
    
    if page > 1:
        keyboard.append([InlineKeyboardButton(text=previous_page_text[lang], callback_data=f"people_list_{page - 1}")])
    if page < total_pages:
        keyboard.append([InlineKeyboardButton(text=next_page_text[lang], callback_data=f"people_list_{page + 1}")])

    keyboard.append([back_btn[lang]])

    send_message = await callback.message.edit_text(
        text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown'
    )
    await state.update_data({ "main_menu_message_id": send_message.message_id })