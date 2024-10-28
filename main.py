from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardRemove
import asyncio

from commands.back_main import back_to_main_menu
from commands.deletedb import delete_db
from commands.start import start_command
from database.db_utils import *

from config import API_TOKEN

from company.company_creation import process_company_name
from company.show_company import show_company
from company.list_company_workers import list_workers
from company.show_departments import show_departments
from company.list_department_workers import list_department_workers
from company.referal_links import show_referal_links
from department.continue_creation import continue_department_creation
from department.department_creation import process_department_name
from department.finish_creation import finish_department_creation
from projects.creation_project import create_project
from registration.birthdate import process_birthdate
from registration.fullname import process_fullname
from registration.lang import set_lang
from registration.phoneNumber import process_phone_number

from settings.company_info import edit_company_name
from settings.company_info.edit_company import edit_company_info
from settings.department import activate_department, delete_department, edit_department_name
from settings.department.edit_department import edit_department
from settings.department.edit_departments_info import edit_departments
from settings.settings import show_settings
from settings.user_info.change_birthdate import changing_birthdate, edit_birthdate
from settings.user_info.change_fullname import changing_fullname, edit_fullname
from settings.user_info.change_lang import changing_lang, edit_lang
from settings.user_info.change_phone import changing_phone_number, edit_phone
from settings.user_info.edit_user import edit_user
from states import *
from tasks.creation_task import create_task

# Initialize bot and storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# callback queries
router.callback_query.register(continue_department_creation, F.data == "continue_department_creation")
router.callback_query.register(finish_department_creation, F.data == "finish_department_creation")
router.callback_query.register(show_company, F.data == "company")
router.callback_query.register(list_workers, F.data.startswith("list_workers"))
router.callback_query.register(show_departments, F.data.startswith("departments"))
router.callback_query.register(list_department_workers, F.data.startswith("show_department_"))
router.callback_query.register(show_referal_links, F.data == "referral_links")
router.callback_query.register(set_lang, F.data.startswith("lang_"))
router.callback_query.register(back_to_main_menu, F.data == "back_to_main_menu")
router.callback_query.register(show_settings, F.data == "settings")
router.callback_query.register(edit_user, F.data == "edit_user_info")
router.callback_query.register(edit_fullname, F.data == "edit_fullname")
router.callback_query.register(edit_phone, F.data == "edit_phone")
router.callback_query.register(edit_birthdate, F.data == "edit_birthdate")
router.callback_query.register(edit_lang, F.data == "edit_language")
router.callback_query.register(changing_lang, F.data.startswith("change_lang_"))
router.callback_query.register(edit_company_info, F.data == "change_company")
router.callback_query.register(edit_company_name.edit_company_name, F.data == "edit_company_name")
router.callback_query.register(edit_departments, F.data.startswith("edit_departments"))
router.callback_query.register(edit_department, F.data.startswith("edit_department_"))
router.callback_query.register(edit_department_name.edit_department_name, F.data.startswith("change_department_name_"))
router.callback_query.register(delete_department.delete_department, F.data.startswith("delete_department_"))
router.callback_query.register(delete_department.confirm_delete_department, F.data.startswith("confirm_delete_department_"))
router.callback_query.register(activate_department.activate_department, F.data.startswith("activate_department_"))
router.callback_query.register(activate_department.confirm_activate_department, F.data.startswith("confirm_activate_department_"))

router.callback_query.register(create_task, F.data == "create_task")

router.callback_query.register(create_project, F.data == "create_project")

# state messages
router.message(StateFilter(RegistrationStates.fullname))(process_fullname)
router.message(StateFilter(RegistrationStates.phone_number))(process_phone_number)
router.message(StateFilter(RegistrationStates.birthdate))(process_birthdate)
router.message(StateFilter(CompanyCreation.company_name))(process_company_name)
router.message(StateFilter(DepartmentCreation.department_name))(process_department_name)
router.message(StateFilter(UserChanges.fullname))(changing_fullname)
router.message(StateFilter(UserChanges.phone_number))(changing_phone_number)
router.message(StateFilter(UserChanges.birthdate))(changing_birthdate)
router.message(StateFilter(CompanyChanges.company_name))(edit_company_name.changing_company_name)
router.message(StateFilter(DepartmentChanges.department_name))(edit_department_name.changing_department_name)

router.message(StateFilter(ProjectCreation.project_name))(create_project.creating_project)

# commands
router.message(F.text == "/start")(start_command)
router.message(F.text == "/deletedb")(delete_db)

async def notify_users_about_restart():
    """Notifies users that the bot is restarting."""
    db_pool = get_db_pool()
    async with db_pool.acquire() as connection:
        users = await connection.fetch("SELECT user_id FROM users")
    
    for user in users:
        try:
            await bot.send_message(user['user_id'], "The bot has been restarted. Please use /start to continue.", reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(f"Error notifying user {user['user_id']}: {e}")

async def main():
    await init_db()  # Initialize the database pool before starting the bot
    dp.include_router(router)  # Register the router with the dispatcher
    await notify_users_about_restart()  # Notify users about the bot restart
    print("Bot started!")  # Debugging info
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
