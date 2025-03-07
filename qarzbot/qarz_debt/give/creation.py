from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user_lang
from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from qarz_states import GiveDebtCreation
from qarz_utils.basic_texts import noactive_btn
from qarz_utils.btns import back_btn

async def give_debt_creation(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    main_message_id = message_data.get("main_message_id")
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if main_message_id != callback.message.message_id:
        # await callback.answer(noactive_btn[lang])
        await callback.answer(f"❗{main_message_id} {callback.message.message_id}")
        return
    
    text = {
        "ru": "❗Вы хотите дать кому-то долг. Пожалуйста, напишите ФИО и номер пользователя в формате \"ФИО - +998XXXXXXXXX\"",
        "uz": "❗Siz kimga qarz bermoqchisiz. Iltimos, FIO va foydalanuvchi raqamini \"FIO - +998XXXXXXXXX\" formatida yozing",
        "oz": "❗Сиз кимга қарз бермоқчисиз. Илтимос, ФИО ва фойдаланувчи рақамини \"ФИО - +998XXXXXXXXX\" форматида ёзинг"
    }
    
    send_text = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_btn[lang]]]))
    await state.update_data({"main_message_id": send_text.message_id})
    await state.set_state(GiveDebtCreation.givedebt_debtor)