from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user
from btns import back_to_settings, edit_user_info_btns

async def edit_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']


    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    await state.clear()
    
    keyboard = []

    for btn in edit_user_info_btns[lang]:
        keyboard.append([types.InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data'])])
    # Create a list of buttons ensuring each item is a list of InlineKeyboardButton
    
    keyboard.append([back_to_settings[lang]])
    # Prepare InlineKeyboardMarkup with the corrected structure
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

    text = "Что вы хотите изменить?" if lang == 'ru' else "Nimani o'zgartirmoqchisiz?" if lang == 'uz' else "What do you want to change?"

    # Send or edit the message
    send_message = await callback.message.edit_text(text, reply_markup=reply_markup)
    await state.update_data(main_menu_message_id=send_message.message_id)
