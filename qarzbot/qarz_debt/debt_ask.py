from qarz_database.db_utils import get_debt, get_user
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_states import RejectionStates
from qarz_utils.main_menu import main_menu
from qarz_utils.basic_texts import borrower_debt_text, debt_404, accept_text, debtor_debt_text, reject_text, noactive_btn
from qarz_database.db_utils import get_db_pool
from qarz_config import API_TOKEN

bot = Bot(token=API_TOKEN)

async def ask_approve_debt(debt_id: int, debt_type: str, message: types.Message, state: FSMContext):
    debt = await get_debt(debt_id)
    user_id = message.chat.id
    user = await get_user(user_id)
    lang = user['lang']
    
    if debt is None:
        await message.answer(debt_404[user['lang']])
        return
    
    db = await get_db_pool()
    async with db.acquire() as connection:
        if debt_type == 'getdebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['borrower_id'])
        if debt_type == 'givedebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['debtor_id'])

        if debt_type == 'getdebt' and debt['borrower_id'] != user['id']:
            await connection.execute("UPDATE debts SET debtor_id = $1 WHERE id = $2", otheruser['id'], debt_id)
        if debt_type == 'givedebt' and debt['debtor_id'] != user['id']:
            await connection.execute("UPDATE debts SET borrower_id = $1 WHERE id = $2", otheruser['id'], debt_id)

    if debt_type == 'getdebt':
        borrower_texts = await borrower_debt_text(debt)  # Await the coroutine
        text = borrower_texts[lang]  # Access the dictionary
    elif debt_type == 'givedebt':
        debtor_texts = await debtor_debt_text(debt)  # Await the coroutine
        text = debtor_texts[lang]  # Access the dictionary


    keyboard = [
        [InlineKeyboardButton(text=accept_text[lang], callback_data=f"approve_{debt_type}_{debt_id}"),
         InlineKeyboardButton(text=reject_text[lang], callback_data=f"reject_{debt_type}_{debt_id}")]
    ]

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": message.message_id})

async def approve_debt(callback: types.CallbackQuery, state: FSMContext):
    debt_id = int(callback.data.split("_")[-1])
    debt_type = callback.data.split("_")[-2]
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']
    
    db = await get_db_pool()

    async with db.acquire() as connection:
        debt = await connection.fetchrow("SELECT * FROM debts WHERE id = $1", debt_id)

        if debt['status'] == 'active':
            await callback.message.edit_text(noactive_btn[lang])
            return
        if debt_type == 'getdebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['borrower_id'])
            await connection.execute("UPDATE debts SET status = 'active', debtor_id = $1 WHERE id = $2", user['id'], debt_id)
        if debt_type == 'givedebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['debtor_id'])
            await connection.execute("UPDATE debts SET status = 'active', borrower_id = $1 WHERE id = $2", user['id'], debt_id)
    text = {
        "ru": f"☑️ Вы подтвердили долг {debt['id']} от {otheruser['fullname']}.",
        "uz": f"☑️ Siz {otheruser['fullname']} dan {debt['id']} qarzni tasdiqladingiz.",
        "oz": f"☑️ Сиз {otheruser['fullname']} дан {debt['id']} қарзни тасдиқладингиз."
    }

    other_text = {
        "ru": f"☑️ {user['fullname']} подтвердил долг {debt['id']}.",
        "uz": f"☑️ {user['fullname']} {debt['id']} qarzni tasdiqladi.",
        "oz": f"☑️ {user['fullname']} {debt['id']} қарзни тасдиқлади."
    }

    keyboard_other_text = {
        "ru": f"👀 Посмотреть детали",
        "uz": f"👀 Tafsilotlarni ko'rish",
        "oz": f"👀 Тафсилотларни кўриш"
    }
    await callback.message.edit_text(text[lang])
    await bot.send_message(otheruser['user_id'], other_text[otheruser['lang']], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=keyboard_other_text[otheruser['lang']], callback_data=f"debt_{debt_id}")]]))
    await state.clear()
    await main_menu(user_id, callback.message.chat.id, state)

async def reject_debt(callback: types.CallbackQuery, state: FSMContext):
    debt_id = int(callback.data.split("_")[-1])
    debt_type = callback.data.split("_")[-2]
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']
    
    db = await get_db_pool()
    async with db.acquire() as connection:
        debt = await connection.fetchrow("SELECT * FROM debts WHERE id = $1", debt_id)
        if debt['status'] == 'active':
            await callback.message.edit_text(noactive_btn[lang])
            return
        if debt_type == 'getdebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['borrower_id'])
            await connection.execute("UPDATE debts SET debtor_id = $1 WHERE id = $2", user['id'], debt_id)
        if debt_type == 'givedebt':
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['debtor_id'])
            await connection.execute("UPDATE debts SET borrower_id = $1 WHERE id = $2", user['id'], debt_id)

    text = {
        "ru": f"❌ Вы отклонили долг {debt['id']} от {otheruser['fullname']}. Пожалуйста, напиши причину.",
        "uz": f"❌ Siz {otheruser['fullname']} dan {debt['id']} qarzni rad etdingiz. Iltimos, sababni yozing.",
        "oz": f"❌ Сиз {otheruser['fullname']} дан {debt['id']} қарзни рад этдингиз. Илтимос, сабабни ёзинг."
    }

    await callback.message.edit_text(text[lang])
    await state.update_data({"rejected_id": debt_id, "rejected_type": debt_type})
    await state.set_state(RejectionStates.reason)