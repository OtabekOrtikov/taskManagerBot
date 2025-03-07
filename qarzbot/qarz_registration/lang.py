from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from qarz_database.db_utils import add_new_user, get_db_pool, get_user
from qarz_states import RegistrationStates
from qarz_utils.missed_fields import missed_field
from qarz_utils.main_menu import main_menu

async def setlang(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]

    if not lang in ["uz", "oz", "ru"]:
        await callback.answer("Неврный язык | Noto'g'ri til | Нотогри тил")
        return

    async with get_db_pool().acquire() as conn:
        await conn.execute(f"UPDATE users SET lang = '{lang}' WHERE user_id = {user_id}")
    text = {
        "ru": "Для регистрации введите ваше имя.",
        "uz": "Ro'yxatdan o'tish uchun ismingizni kiriting.",
        "oz": "Рўйхатдан ўтиш учун исмингизни киритинг."
    }
    await callback.message.edit_text(text=text[lang])
    await state.set_state(RegistrationStates.fullname)