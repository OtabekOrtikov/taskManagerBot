from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter
import asyncio

from commands.back_to_main import back_to_main_menu
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
from registration.fullname import process_fullname
from registration.lang import set_lang
from registration.phoneNumber import process_phone_number

from states import CompanyCreation, DepartmentCreation, RegistrationStates

# Initialize bot and storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

router.callback_query.register(continue_department_creation, F.data == "continue_department_creation")
router.callback_query.register(finish_department_creation, F.data == "finish_department_creation")
router.callback_query.register(show_company, F.data == "company")
router.callback_query.register(list_workers, F.data.startswith("list_workers"))
router.callback_query.register(show_departments, F.data.startswith("departments"))
router.callback_query.register(list_department_workers, F.data.startswith("show_department_"))
router.callback_query.register(show_referal_links, F.data == "referral_links")
router.callback_query.register(set_lang, F.data.startswith("lang_"))
router.callback_query.register(back_to_main_menu, F.data == "back_to_main_menu")
router.message(StateFilter(RegistrationStates.fullname))(process_fullname)
router.message(StateFilter(RegistrationStates.phone_number))(process_phone_number)
router.message(StateFilter(CompanyCreation.company_name))(process_company_name)
router.message(StateFilter(DepartmentCreation.department_name))(process_department_name)
router.message(F.text == "/start")(start_command)
router.message(F.text == "/deletedb")(delete_db)

async def notify_users_about_restart():
    """Notifies users that the bot is restarting."""
    db_pool = get_db_pool()
    async with db_pool.acquire() as connection:
        users = await connection.fetch("SELECT user_id FROM users")
    
    for user in users:
        try:
            await bot.send_message(user['user_id'], "The bot has been restarted. Please use /start to continue.")
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
