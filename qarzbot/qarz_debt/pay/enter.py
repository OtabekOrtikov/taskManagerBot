from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from qarz_database.db_utils import get_user, get_debt, get_db_pool, get_user_lang
from qarz_utils.basic_texts import noactive_btn, amount_entered_successfully, back_text, enter_valid_amount, debt_completed
from qarz_states import EnterAmountState
from qarz_utils.main_menu import main_menu

async def enter_amount(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_message_id")
    user = await get_user(callback.from_user.id)
    lang = user['lang']

    if callback.message.message_id != last_button_message_id:
        await callback.answer(noactive_btn[lang])
        return

    data = callback.data.split('_')
    debt_id = int(data[-1])

    await state.update_data({"amount_debt_id": debt_id})

    text = {
        "ru": "❗ Введите сумму, которую должник вам заплатил.",
        "uz": "❗ Qarz bergan shaxsga to'langan summani kiriting.",
        "oz": "❗ Қарз берган шахсга тўланган суммани киритинг."
    }

    keyboard = [[InlineKeyboardButton(text=back_text[lang], callback_data=f"debt_{debt_id}")]]

    send_message = await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data({"main_message_id": send_message.message_id})
    await state.set_state(EnterAmountState.entered_amount)

import json
from datetime import datetime

async def process_entered_amount(message: types.Message, state: FSMContext):
    try:
        # Validate the input number
        entered_amount = message.text.replace(" ", "").replace(",", ".")
        if not entered_amount.replace('.', '', 1).isdigit():  # Allow decimal points
            await message.answer(enter_valid_amount[lang])
            return

        entered_amount = float(entered_amount)

        # Fetch data from state and database
        data = await state.get_data()
        debt_id = int(data.get("amount_debt_id"))
        user_id = message.from_user.id
        lang = await get_user_lang(user_id)
        debt = await get_debt(debt_id)

        # Extract required debt details
        full_amount = debt['full_amount']
        paid_amount = json.loads(debt.get('paid_amount', "{}"))  # Default to empty dict if None

        # Calculate remaining unpaid amount
        total_paid = sum(paid_amount.values())
        remaining_amount = full_amount - total_paid

        if entered_amount > remaining_amount:
            error_text = {
                "ru": f"❗ Вы ввели сумму больше, чем осталось заплатить ({remaining_amount} {debt['currency']}).",
                "uz": f"❗ Siz kiritgan summa qolgan to'lanishi kerak bo'lgan summadan ({remaining_amount} {debt['currency']}) ko'p.",
                "oz": f"❗ Сиз киритган сумма қолган тўланиши керак бўлган суммадан ({remaining_amount} {debt['currency']}) кўп."
            }
            await message.answer(error_text[lang])
            return

        # Update the paid amounts
        timestamp = datetime.now().strftime("%d.%m.%Y")
        if timestamp in paid_amount:
            paid_amount[timestamp] += entered_amount
        else:
            paid_amount[timestamp] = entered_amount

        # Check if debt is fully paid
        total_paid += entered_amount
        is_completed = total_paid >= full_amount

        # Prepare updated JSON
        divided_paid = json.dumps(paid_amount)

        # Update the database
        db = await get_db_pool()
        async with db.acquire() as conn:
            await conn.execute(
                "UPDATE debts SET paid_amount = $1, status = $2 WHERE id = $3",
                divided_paid,
                'completed' if is_completed else 'active',
                debt_id
            )

        # Clear the state and notify the user
        await state.update_data()
        if is_completed:
            await message.answer(debt_completed(debt_id)[lang])
        else:
            await message.answer(amount_entered_successfully[lang])
        await state.clear()
        await main_menu(user_id, message.chat.id, state)

    except Exception as e:
        error_text = {
            "ru": "❗ Произошла ошибка. Попробуйте еще раз.",
            "uz": "❗ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            "oz": "❗ Хатолик юз берди. Қайтадан уриниб кўринг."
        }
        # Handle unexpected errors gracefully
        await message.answer(error_text[lang])
        print(f"Error processing entered amount: {e}")
