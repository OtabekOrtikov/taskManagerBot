import datetime
from aiogram.fsm.context import FSMContext
from qarz_config import API_TOKEN
from qarz_database.db_utils import get_db_pool, get_user_lang
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

bot = Bot(token=API_TOKEN)

from qarz_states import RegistrationStates
from qarz_utils.basic_texts import invalid_birthdate as error_text, accept_text, rules_links, rules_text

async def process_birthdate(message: types.Message, state: FSMContext):
    birthdate = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    try:
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", birthdate):
            raise ValueError(error_text[lang])

        date_obj = datetime.datetime.strptime(birthdate, "%d.%m.%Y")

        if date_obj.year < 1920 or date_obj.year > 2020:
            raise ValueError(error_text[lang])

        async with get_db_pool().acquire() as connection:
            await connection.execute("UPDATE users SET birthdate = $1 WHERE user_id = $2", date_obj, user_id)
        text = {
            "ru": "Отлично! 📚Теперь осталось прочитать и принять правила бота. Нажмите на кнопку ниже, чтобы перейти к правилам.",
            "uz": "Yaxshi! 📚Endi bot qoidalarini o'qib o'ting va qabul qiling. Quyidagi tugmani bosib qoidalarga o'ting.",
            "oz": "Яхши! 📚Энди бот қоидаларини ўқиб ўтинг ва қабул қилинг. Қуйидаги тугмани босиб қоидаларга ўтинг."
        }
        sendmessage = await message.answer(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rules_text[lang], url=rules_links[lang])],
            [InlineKeyboardButton(text=accept_text[lang], callback_data="accept_rules")]
        ]))
        await state.set_state(RegistrationStates.approve_rules)
        await state.update_data(main_message_id = sendmessage.message_id)
    except ValueError:
        await message.answer(error_text[lang])
        return