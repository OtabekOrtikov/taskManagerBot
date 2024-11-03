from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user
import states

async def asking_missed_fields(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get('lang', 'ru')  # Default to English if 'lang' is missing

    text = {
        'en': "You have missed some fields. Please fill them in.",
        'ru': "Вы пропустили некоторые поля. Пожалуйста, заполните их.",
        'uz': "Siz ba'zi maydonlarni o'tkazdingiz. Iltimos, ularni to'ldiring."
    }

    fullname_text = {
        'en': "Please enter your full name.",
        'ru': "Пожалуйста, введите ваше полное имя.",
        'uz': "Iltimos, to'liq ismingizni kiriting."
    }

    phone_number_text = {
        'en': "Please enter your phone number.",
        'ru': "Пожалуйста, введите ваш номер телефона.",
        'uz': "Iltimos, telefon raqamingizni kiriting."
    }

    birthdate_text = {
        'en': "Please enter your birthdate in the format DD.MM.YYYY.",
        'ru': "Пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ.",
        'uz': "Tug'ilgan kun bo'yicha sana kiriting: КК.ОО.YYYY."
    }

    company_name_text = {
        'en': "Please enter your company name.",
        'ru': "Пожалуйста, введите название вашей компании.",
        'uz': "Iltimos, kompaniya nomini kiriting."
    }

    # Checking each field and setting the appropriate state if missing
    if not user.get('fullname'):
        await message.answer(text[lang])
        await message.answer(fullname_text[lang])
        await state.set_state(states.RegistrationStates.fullname)
        return False
    if not user.get('phone_number'):
        await message.answer(text[lang])
        await message.answer(phone_number_text[lang])
        await state.set_state(states.RegistrationStates.phone_number)
        return False
    if not user.get('birthdate'):
        await message.answer(text[lang])
        await message.answer(birthdate_text[lang])
        await state.set_state(states.RegistrationStates.birthdate)
        return False
    if not user.get('company_id'):
        await message.answer(text[lang])
        await message.answer(company_name_text[lang])
        await state.set_state(states.CompanyCreation.company_name)
        return False
    
    # Clear the state if all fields are filled
    await state.clear()
    return True
