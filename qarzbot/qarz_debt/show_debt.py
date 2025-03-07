from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user, get_debt
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import noactive_btn, debt_text

async def show_debt(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    

    data = callback.data.split("_")
    debt_id = int(data[-1])

    debt = await get_debt(debt_id)
    
    text = await debt_text(debt)

    keyboard = []

    keyboard_text = {
        "uz": {
            "mark_paid": "☑️ To'lovni to'langan deb belgilash",
            "enter_amount": "🖊️ Miqdorni kiriting",
        },
        "ru": {
            "mark_paid": "☑️ Отметить как оплаченный",
            "enter_amount": "🖊️ Введите сумму",
        },
        "oz": {
            "mark_paid": "☑️ Тўловни тўланган деб белгилаш",
            "enter_amount": "🖊️ Миқдорни киритинг",
        }
    }

    if debt['status'] == 'active':
        if debt['debtor_id'] == user['id']:
            keyboard.append([InlineKeyboardButton(text=keyboard_text[lang]["mark_paid"], callback_data=f"mark_paid_{debt_id}")])
        keyboard.append([InlineKeyboardButton(text=keyboard_text[lang]["enter_amount"], callback_data=f"enter_amount_{debt_id}")])

    keyboard.append([back_btn[lang]])

    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})