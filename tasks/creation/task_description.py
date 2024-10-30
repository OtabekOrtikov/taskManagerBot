from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utils import get_user_lang
from btns import back_to_main
from states import TaskCreation

async def process_task_description(message: types.Message, state: FSMContext):
    task_description = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    await state.update_data(task_description=task_description)
    keyboard = []

    if lang == 'en':
        send_text = "Great, now please enter the start date of the task in the format: **dd.mm** or **dd.mm.yy**\n\nP.s. If you want to set the start date to today, just click the button below."
        keyboard.append([InlineKeyboardButton(text="Set today", callback_data="set_today")])
    elif lang == 'ru':
        send_text = "Отлично, теперь введите дату начала задачи в формате: **дд.мм** или **дд.мм.гг**\n\nP.s. Если вы хотите установить дату начала на сегодня, просто нажмите кнопку ниже."
        keyboard.append([InlineKeyboardButton(text="Установить сегодня", callback_data="set_today")])
    elif lang == 'uz':
        send_text = "Ajoyib, endi vazifa boshlash sanasini quyidagi formatda kiriting: **kk.oo** yoki **kk.oo.yy**\n\nP.s. Agar siz boshlash sanasini bugunga sozlashni xohlaysiz, pastdagi tugmani bosing."
        keyboard.append([InlineKeyboardButton(text="Bugunni qo'yish", callback_data="set_today")])
    
    keyboard.append([back_to_main[lang]])
    await message.answer(send_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=message.message_id+1)
    await state.set_state(TaskCreation.start_date)


