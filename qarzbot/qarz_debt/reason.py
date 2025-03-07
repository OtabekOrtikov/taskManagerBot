from qarz_database.db_utils import get_db_pool, get_debt, get_user
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from qarz_config import API_TOKEN
from qarz_utils.main_menu import main_menu

bot = Bot(token=API_TOKEN)

async def process_reason(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    reason = message.text
    data = await state.get_data()
    debt_id = data.get("rejected_id")
    
    db = await get_db_pool()

    async with db.acquire() as connection:
        debt = await get_debt(debt_id)
        if debt['borrower_id'] == user_id:
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['debtor_id'])
        else:
            otheruser = await connection.fetchrow("SELECT * FROM users WHERE id = $1", debt['borrower_id'])

    if data.get("rejected_type") == 'getdebt':
        text = {
            "ru": f"❗Ваш запрос на взятие долга отклонен пользователем {otheruser['fullname']}. 📑 Причина: {reason}",
            "uz": f"❗Sizning qarz so'rovingiz {otheruser['fullname']} tomonidan rad etildi. 📑 Sababi: {reason}",
            "oz": f"❗Сизнинг қарз сўровингиз {otheruser['fullname']} томонидан рад этилди. 📑 Сабаби: {reason}"
        }
    else:
        text = {
            "ru": f"❗Ваш запрос на выдачу долга отклонен пользователем {otheruser['fullname']}. 📑 Причина: {reason}",
            "uz": f"❗Sizning qarz so'rovingiz {otheruser['fullname']} tomonidan rad etildi. 📑 Sababi: {reason}",
            "oz": f"❗Сизнинг қарз сўровингиз {otheruser['fullname']} томонидан рад этилди. 📑 Сабаби: {reason}"
        }

    rejected_text = {
        "ru": f"❗Вы отклонили запрос на долг под причиной: {reason}",
        "uz": f"❗Siz qarz so'rovini rad etdingiz. Sababi: {reason}",
        "oz": f"❗Сиз қарз сўровини рад этишингизни сабаби: {reason}"
    }

    await message.reply_to_message(rejected_text[lang])
    await bot.send_message(otheruser['user_id'], text[lang])
    await state.clear()
    await main_menu(user_id, message.chat.id, state)