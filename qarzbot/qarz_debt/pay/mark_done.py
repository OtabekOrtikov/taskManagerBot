from datetime import datetime
import json
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user, get_debt, get_db_pool, get_user_by_id, get_user_lang
from qarz_utils.btns import back_btn
from qarz_utils.basic_texts import noactive_btn, debt_completed
from qarz_states import EnterAmountState
from qarz_utils.main_menu import main_menu
from qarz_config import API_TOKEN

bot = Bot(token=API_TOKEN)

async def mark_done(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return

    data = callback.data.split('_')
    debt_id = int(data[-1])

    await state.update_data({"amount_debt_id": debt_id})

    text = {
        "ru": "❗ Вы уверены, что долг погашен?",
        "uz": "❗ Qarz toʻlanganligiga ishonchingiz komilmiя?",
        "oz": "❗ Қарз тўланганлигига ишончингиз комилмиз?"
    }

    keyboard_text = {
        "yes": {
            "ru": "☑️Да",
            "uz": "☑️Ha",
            "oz": "☑️Ҳа"
        },
        "no": {
            "ru": "❌Нет",
            "uz": "❌Yo'q",
            "oz": "❌Йўқ"
        }
    }

    keyboard = [
        [InlineKeyboardButton(text=keyboard_text["yes"][lang], callback_data=f"mark_done_yes_{debt_id}"),
         InlineKeyboardButton(text=keyboard_text["no"][lang], callback_data=f"debt_{debt_id}")],
        [back_btn[lang]]
    ]

    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})

async def mark_done_yes(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    debt_id = int(message_data.get("amount_debt_id"))
    debt = await get_debt(debt_id)
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return
    otheruser = await get_user_by_id(debt['borrower_id']) if debt['debtor_id'] == user['id'] else await get_user_by_id(debt['debtor_id'])
    paid_amount = json.loads(debt.get("paid_amount", "{}"))
    full_amount = debt['full_amount']

    total_paid = sum(paid_amount.values())
    remaining_amount = full_amount - total_paid

    timestamp = datetime.now().strftime("%d.%m.%Y")
    if timestamp in paid_amount:
        paid_amount[timestamp] += remaining_amount
    else:
        paid_amount[timestamp] = remaining_amount

    total_paid += remaining_amount

    divided_paid = json.dumps(paid_amount)

    db = await get_db_pool()
    async with db.acquire() as conn:
        await conn.execute(
            "UPDATE debts SET paid_amount = $1, status = $2 WHERE id = $3",
            divided_paid,
            'completed',
            debt_id
        )

    await callback.message.edit_text(debt_completed(debt_id)[lang])
    await bot.send_message(otheruser['user_id'], debt_completed(debt_id)[lang])
    await main_menu(user['user_id'], callback.message.chat.id, state)