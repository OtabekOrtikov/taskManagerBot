from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_database.db_utils import get_user, get_db_pool
from qarz_utils.basic_texts import borrower_debt_text, accept_text, reject_text
from qarz_config import API_TOKEN
from qarz_utils.btns import back_btn

bot = Bot(token=API_TOKEN)

async def process_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This message is not active")
        return

    debt_id = int(callback.data.split("_")[-1])
    debtor_id = int(callback.data.split("_")[-2])

    async with get_db_pool().acquire() as connection:
        await connection.execute("UPDATE debts SET debtor_id = $1 WHERE id = $2", debtor_id, debt_id)
        debtor = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debtor_id)
        debt = await connection.fetchrow("SELECT * FROM debts WHERE id = $1", debt_id)

    text = {
        "ru": f"☑️ Отлично, мы отправили запрос на подтверждение долга {debtor['fullname']}. Мы уведомим вас, когда долг будет подтвержден.",
        "uz": f"☑️ Ajoyib, biz {debtor['fullname']} ga qarzni tasdiqlash so'roqini yubordik. Qarz tasdiqlanib bo'lganda sizni xabardor qilamiz.",
        "oz": f"☑️ Ажойиб, биз {debtor['fullname']} га қарзни тасдиқлаш сўроқини юбордик. Қарз тасдиқланиб бўлганда сизни хабардор қиламиз."
    }

    keyboard = [
        [back_btn[lang]]
    ]

    send_message = await callback.message.edit_text(text[user['lang']], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.clear()
    await state.update_data({"main_message_id": send_message.message_id})

    debtor_text = borrower_debt_text(debt, user)[lang]

    await bot.send_message(debtor['user_id'], debtor_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=accept_text[lang], callback_data=f"approve_getdebt_{debt_id}"),
         InlineKeyboardButton(text=reject_text[lang], callback_data=f"reject_getdebt_{debt_id}")]
    ]))
    