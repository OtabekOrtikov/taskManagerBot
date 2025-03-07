from aiogram import types
from aiogram.fsm.context import FSMContext
from qarz_database.db_utils import get_user
from qarz_states import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from qarz_utils.basic_texts import missing_field as text, accept_text, rules_links, rules_text

async def missed_field(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user['lang']  # Default to English if 'lang' is missing

    # Checking each field and setting the appropriate state if missing
    if not user.get('fullname'):
        await message.answer(text[lang]['basic'])
        await message.answer(text[lang]['fullname'])
        await state.set_state(RegistrationStates.fullname)
        return False
    if not user.get('phone_number'):
        await message.answer(text[lang]['basic'])
        await message.answer(text[lang]['phone_number'])
        await state.set_state(RegistrationStates.phone_number)
        return False
    if not user.get('birthdate'):
        await message.answer(text[lang]['basic'])
        await message.answer(text[lang]['birthdate'])
        await state.set_state(RegistrationStates.birthdate)
        return False
    if not user.get('accepted_rules'):
        await message.answer(text[lang]['basic'])
        await message.answer(text=text[lang]['rules'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rules_text[lang], url=rules_links[lang])],
            [InlineKeyboardButton(text=accept_text[lang], callback_data='accept_rules')]
        ]))
        return False
    
    # Clear the state if all fields are filled
    await state.clear()
    return True
