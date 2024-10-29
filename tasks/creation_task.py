from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_utils import get_user, get_db_pool
from btns import back_to_main
from states import TaskCreation

async def create_task(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    db_pool = get_db_pool()

    async with db_pool.acquire() as connection:
        projects = await connection.fetch("SELECT * FROM project WHERE boss_id = $1", user['id'])

    if projects:
        project_keyboard = []
        for project in projects:
            project_keyboard.append([
                InlineKeyboardButton(text=project['project_name'], callback_data=f"create_project_task_{project['id']}")
            ])
        
        # Add skip option based on language
        if lang == "ru":
            project_keyboard.append([InlineKeyboardButton(text="Пропустить", callback_data="skip_project_task_creation")])
            text = "Выберите на какой проект хотите создать задачу или вы можете пропустить эту часть.\n\nПропуская эту часть, вы будете создавать задачу для сотрудника вашей компании."
        elif lang == "uz":
            project_keyboard.append([InlineKeyboardButton(text="O'tkazib yuborish", callback_data="skip_project_task_creation")])
            text = "Vazifa yaratish uchun qaysi loyihada yaratmoqchisiz yoki bu qismni o'tkazib yuborishingiz mumkin.\n\nBu qismni o'tkazib yuborsangiz, siz kompaniyangizning xodimiga vazifa yaratasiz."
        elif lang == 'en':
            project_keyboard.append([InlineKeyboardButton(text="Skip", callback_data="skip_project_task_creation")])
            text = "Choose on which project you want to create a task or you can skip this part.\n\nBy skipping this part, you will create a task for an employee of your company."
        
        # Add back button
        project_keyboard.append([back_to_main[lang]])
        
        send_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=project_keyboard))
        await state.update_data(main_menu_message_id=send_message.message_id)
    else:
        if lang == "ru":
            send_message = await callback.message.edit_text("У вас нет проектов. Поэтому вы создаете задачу для сотрудника вашей компании.\nВведите название задачи.", 
                                                            reply_markup=InlineKeyboardMarkup(
                                                                inline_keyboard=[
                                                                    [back_to_main[lang]]
                                                                ]
                                                            ))
        elif lang == "uz":
            send_message = await callback.message.edit_text("Sizda loyihalar yo'q. Shuning uchun siz kompaniyangizning xodimi uchun vazifa yaratasiz.\nVazifa nomini kiriting.", 
                                                            reply_markup=InlineKeyboardMarkup(
                                                                inline_keyboard=[
                                                                    [back_to_main[lang]]
                                                                ]
                                                            ))
        elif lang == 'en':
            send_message = await callback.message.edit_text("You don't have any projects. Therefore, you are creating a task for an employee of your company.\nEnter the task name.", 
                                                            reply_markup=InlineKeyboardMarkup(
                                                                inline_keyboard=[
                                                                    [back_to_main[lang]]
                                                                ]
                                                            ))
        await state.set_state(TaskCreation.task_title)
        await state.update_data(main_menu_message_id=send_message.message_id)
