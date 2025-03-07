from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from qarz_database.db_utils import add_new_user, get_debt, get_user
from qarz_states import RegistrationStates
from qarz_debt.debt_ask import ask_approve_debt
from qarz_utils.main_menu import main_menu
from qarz_utils.missed_fields import missed_field
from qarz_utils.basic_texts import invalid_referal, welcome_text
from qarz_utils.btns import language_btn

async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    user = await get_user(user_id)
    args = message.text.split(" ", 1)

    await state.update_data(main_menu_message_id=0)

    debt_type = None
    debt_id = None

    if len(args) > 1 and args[1]:
        try:
            params = args[1]
            print(params.split("_"))
            debt_type, debt_id = params.split("_")
        except Exception:
            await message.reply(invalid_referal[user['lang']])
            return
    debt_id = int(debt_id) if debt_id else None

    if debt_type and debt_id:
        debt = await get_debt(debt_id)

        if not debt or debt['status'] != 'draft':
            await message.answer(invalid_referal[user['lang']])
            return
        
        if user is None:
            await add_new_user(user_id)

            await message.answer(welcome_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=language_btn))
            await state.set_state(RegistrationStates.lang)
            await state.update_data({"waiting_for_approve": debt_id, "waiting_for_approve_type": debt_type})
        else:
            if not await missed_field(message, state):
                return
            if debt_type == 'getdebt':
                if debt['borrower_id'] == user['id']:
                    await main_menu(user_id, message.chat.id, state)
                else:
                    await ask_approve_debt(debt_id, debt_type, message, state)
            if debt_type == 'givedebt':
                if debt['debtor_id'] == user['id']:
                    await main_menu(user_id, message.chat.id, state)
                else:
                    await ask_approve_debt(debt_id, debt_type, message, state)
    else:
        if user is None:
            await add_new_user(user_id)

            await message.answer(welcome_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=language_btn))
            await state.set_state(RegistrationStates.lang)
        else:
            if not await missed_field(message, state):
                return
            await main_menu(user_id, message.chat.id, state)
    
        





