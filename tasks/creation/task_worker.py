from aiogram import types
from aiogram.fsm.context import FSMContext
from database.db_utils import get_user_lang
from btns import priority_btns
from states import TaskCreation

async def process_task_worker(callback: types.CallbackQuery, state: FSMContext):
    last_button_message_id = (await state.get_data()).get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer(f"This button is no longer active.{last_button_message_id} {callback.message.message_id}")
        return

    task_assignee_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    await state.update_data(task_assignee_id=task_assignee_id)

    if lang == 'en':
        send_text = "Great! Now, please select the priority of the task."
    elif lang == 'ru':
        send_text = "Отлично! Теперь, пожалуйста, выберите приоритет задания."
    elif lang == 'uz':
        send_text = "Ajoyib! Endi, iltimos, vazifaning ustuvorligini tanlang."

    await callback.message.edit_text(send_text, reply_markup=priority_btns[lang])
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskCreation.priority)