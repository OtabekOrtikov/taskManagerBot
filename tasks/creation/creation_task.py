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


    if user['role_id'] == 1:
        if projects:
            project_keyboard = []
            for project in projects:
                project_keyboard.append([
                    InlineKeyboardButton(text=project['project_name'], callback_data=f"create_project_task_{project['id']}")
                ])
            
            text = {
                "en": "Choose on which project you want to create a task or you can skip this part.\n\nBy skipping this part, you will create a task for an employee of your company.",
                "ru": "Выберите на какой проект хотите создать задачу или вы можете пропустить эту часть.\n\nПропуская эту часть, вы будете создавать задачу для сотрудника вашей компании.",
                "uz": "Vazifa yaratish uchun qaysi loyihada yaratmoqchisiz yoki bu qismni o'tkazib yuborishingiz mumkin.\n\nBu qismni o'tkazib yuborsangiz, siz kompaniyangizning xodimiga vazifa yaratasiz."
            }
            keyboard_text = {
                "en": "Skip",
                "ru": "Пропустить",
                "uz": "O'tkazib yuborish"
            }
            # Add skip option based on language
            project_keyboard.append([InlineKeyboardButton(text=keyboard_text[lang], callback_data="skip_project_task_creation")])
            # Add back button
            project_keyboard.append([back_to_main[lang]])
            
            send_message = await callback.message.edit_text(text=text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=project_keyboard))
            await state.update_data(main_menu_message_id=send_message.message_id)
        else:
            text = {
                "en": "You don't have any projects. Therefore, you are creating a task for an employee of your company.\nEnter the task name. Maximum 30 characters.",
                "ru": "У вас нет проектов. Поэтому вы создаете задачу для сотрудника вашей компании.\nВведите название задачи. Максимум 30 символов.",
                "uz": "Sizda loyihalar yo'q. Shuning uchun siz kompaniyangizning xodimi uchun vazifa yaratasiz.\nVazifa nomini kiriting. Maksimum 30 belgi."
            }
            send_message = await callback.message.edit_text(text=text[lang], 
                                                            reply_markup=InlineKeyboardMarkup(
                                                                inline_keyboard=[
                                                                    [back_to_main[lang]]
                                                                ]
                                                            ))
            await state.set_state(TaskCreation.task_title)
            await state.update_data(main_menu_message_id=send_message.message_id)
    else:
        text = {
            "en": "Enter the task name. Maximum 30 characters.",
            "ru": "Введите название задачи. Максимум 30 символов.",
            "uz": "Vazifa nomini kiriting. Maksimum 30 belgi."
        }
        send_message = await callback.message.edit_text(text=text[lang], 
                                                        reply_markup=InlineKeyboardMarkup(
                                                            inline_keyboard=[
                                                                [back_to_main[lang]]
                                                            ]
                                                        ))
        await state.set_state(TaskCreation.task_title)
        await state.update_data(main_menu_message_id=send_message.message_id)