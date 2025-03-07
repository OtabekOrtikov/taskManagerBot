from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from aiogram.filters import StateFilter

from qarz_config import API_TOKEN
from qarz_scheduler.scheduler import scheduler
from qarz_states import *
from qarz_database.db_utils import init_db

# Initialize bot and storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Commands
from qarz_commands.start import start_command
router.message(F.text.startswith("/start"))(start_command)

# Main menu
from qarz_utils.back_main import back_to_main_menu
router.callback_query(F.data == "back")(back_to_main_menu)

# registraion
## lang
from qarz_registration.lang import setlang
router.callback_query(F.data.startswith("lang"))(setlang)
## fullname
from qarz_registration.fullname import process_fullname
router.message(StateFilter(RegistrationStates.fullname))(process_fullname)
## phone_number
from qarz_registration.phone_number import process_phone_number
router.message(StateFilter(RegistrationStates.phone_number))(process_phone_number)
## birthdate
from qarz_registration.birthdate import process_birthdate
router.message(StateFilter(RegistrationStates.birthdate))(process_birthdate)
## rules
from qarz_registration.accept_rules import process_accept_rules
router.callback_query(F.data.startswith("accept_rules"))(process_accept_rules)

# Get debt
## creation
from qarz_debt.get.creation import get_debt_creation
router.callback_query(F.data.startswith("get_debt"))(get_debt_creation)
### debtor, phone
from qarz_debt.get.creditor import process_creditor
router.message(StateFilter(GetDebtCreation.getdebt_creditor))(process_creditor)
### amount
from qarz_debt.get.amount import process_get_amount
router.message(StateFilter(GetDebtCreation.getdebt_amount))(process_get_amount)
### currency
from qarz_debt.get.currency import process_get_currency
router.callback_query(F.data.startswith("getdebt_currency"))(process_get_currency)
### loan date
from qarz_debt.get.loan_date import process_loan_date_getdebt
router.message(StateFilter(GetDebtCreation.getdebt_loan_date))(process_loan_date_getdebt)
### set today getdebt
from qarz_debt.get.set_today import set_today_getdebt
router.callback_query(F.data.startswith("set_today_getdebt"))(set_today_getdebt)
### due date
#### divider
from qarz_debt.get.due_dates.divider import handle_division_choice
router.callback_query(F.data.startswith("getdebt_divide"))(handle_division_choice)
#### handle date
from qarz_debt.get.due_dates.handle_date import handle_due_date_entry
router.message(StateFilter(GetDebtCreation.getdebt_due_date))(handle_due_date_entry)
#### stop due date
from qarz_debt.get.due_dates.stop import getdebt_stop_due_date
router.callback_query(F.data.startswith("getdebt_finish_due"))(getdebt_stop_due_date)
### comment
#### with comment
from qarz_debt.get.comment import process_comment_getdebt
router.message(StateFilter(GetDebtCreation.getdebt_comment))(process_comment_getdebt)
#### skip comment
from qarz_debt.get.skip_comment import skip_comment_getdebt
router.callback_query(F.data.startswith("getdebt_skip_comment"))(skip_comment_getdebt)
### selecting user
#### process user
from qarz_debt.get.selected_user import process_user
router.callback_query(F.data.startswith("getdebt_"))(process_user)
#### user list
from qarz_debt.get.user_list import getdebt_userlist
router.callback_query(F.data.startswith("getdebt_userlist"))(getdebt_userlist)
### getting referal
#### approve debt
from qarz_debt.debt_ask import approve_debt
router.callback_query(F.data.startswith("approve_"))(approve_debt)
#### reject debt
from qarz_debt.debt_ask import reject_debt
router.callback_query(F.data.startswith("reject_"))(reject_debt)
#### rejection reason
from qarz_debt.reason import process_reason
router.message(StateFilter(RejectionStates.reason))(process_reason)

# Give debt
## creation
from qarz_debt.give.creation import give_debt_creation
router.callback_query(F.data.startswith("give_debt"))(give_debt_creation)
### borrower, phone
from qarz_debt.give.borrower import process_borrower
router.message(StateFilter(GiveDebtCreation.givedebt_debtor))(process_borrower)
### amount
from qarz_debt.give.amount import process_give_amount
router.message(StateFilter(GiveDebtCreation.givedebt_amount))(process_give_amount)
### currency
from qarz_debt.give.currency import process_give_currency
router.callback_query(F.data.startswith("givedebt_currency"))(process_give_currency)
### loan date
from qarz_debt.give.loan_date import process_loan_date_givedebt
router.message(StateFilter(GiveDebtCreation.givedebt_loan_date))(process_loan_date_givedebt)
### set today givedebt
from qarz_debt.give.set_today import set_today_givedebt
router.callback_query(F.data.startswith("set_today_givedebt"))(set_today_givedebt)
### due date
#### divider
from qarz_debt.give.due_dates.divider import handle_division_choice
router.callback_query(F.data.startswith("givedebt_divide"))(handle_division_choice)
#### handle date
from qarz_debt.give.due_dates.handle_date import handle_due_date_entry
router.message(StateFilter(GiveDebtCreation.givedebt_due_date))(handle_due_date_entry)
#### stop due date
from qarz_debt.give.due_dates.stop import givedebt_stop_due_date
router.callback_query(F.data.startswith("givedebt_finish_due"))(givedebt_stop_due_date)
### comment
#### with comment
from qarz_debt.give.comment import process_comment_givedebt
router.message(StateFilter(GiveDebtCreation.givedebt_comment))(process_comment_givedebt)
#### skip comment
from qarz_debt.give.skip_comment import skip_comment_givedebt
router.callback_query(F.data.startswith("givedebt_skip_comment"))(skip_comment_givedebt)
### selecting user
#### process user
from qarz_debt.give.selected_user import process_user
router.callback_query(F.data.startswith("givedebt_"))(process_user)
#### user list
from qarz_debt.give.user_list import givedebt_userlist
router.callback_query(F.data.startswith("givedebt_userlist"))(givedebt_userlist)

# Given debts list
## list
from qarz_lists.given_debts import given_list
router.callback_query(F.data.startswith("given_debts"))(given_list)

# Taken debts list
## list
from qarz_lists.taken_debts import get_list
router.callback_query(F.data.startswith("taken_debts"))(get_list)

# People list
## list
from qarz_lists.people import show_people
router.callback_query(F.data.startswith("people_list"))(show_people)
## user info
from qarz_lists.user import show_user
router.callback_query(F.data.startswith("user_"))(show_user)
## show taken/given debts by user
from qarz_lists.show_list import show_list
router.callback_query(F.data.startswith("show_"))(show_list)

# Debt
## show debt
from qarz_debt.show_debt import show_debt
router.callback_query(F.data.startswith("debt_"))(show_debt)
## enter amount
from qarz_debt.pay.enter import enter_amount
router.callback_query(F.data.startswith("enter_amount"))(enter_amount)
## process entered amount
from qarz_debt.pay.enter import process_entered_amount
router.message(StateFilter(EnterAmountState.entered_amount))(process_entered_amount)
## mark as paid
from qarz_debt.pay.mark_done import mark_done
router.callback_query(F.data.startswith("mark_paid"))(mark_done)
###
from qarz_debt.pay.mark_done import mark_done_yes
router.callback_query(F.data.startswith("mark_done_yes_"))(mark_done_yes)

from qarz_states import ChangeUserData

# Settings
## show settings
from qarz_settings.setting import show_settings
router.callback_query(F.data.startswith("settings"))(show_settings)
## show user settings
from qarz_settings.show_user import show_usersettings
router.callback_query(F.data.startswith("userdata"))(show_usersettings)
### change user data
from qarz_settings.edit_user import edit_user_data
router.callback_query(F.data.startswith("change_user_data"))(edit_user_data)
#### select field
from qarz_settings.edit_user import change_user
router.callback_query(F.data.startswith("changedata_name"))(change_user)
##### process user name
from qarz_settings.edit_user import process_user_name
router.message(StateFilter(ChangeUserData.user_name))(process_user_name)
##### process user phone
from qarz_settings.edit_user import process_user_phone
router.message(StateFilter(ChangeUserData.user_phone))(process_user_phone)
##### process user birthday
from qarz_settings.edit_user import process_user_birthday
router.message(StateFilter(ChangeUserData.user_birthday))(process_user_birthday)

# Import all filter handlers
from qarz_settings.filter import (
    filter_settings,
    filter_date, filter_date_process,
    filter_currency, filter_currency_process,
    filter_status, filter_status_process
)

router.callback_query.register(filter_settings, F.data.startswith("filter_settings"))

# 📌 Register Date Filter
router.callback_query.register(filter_date, F.data == "filter_date")
router.callback_query.register(filter_date_process, F.data.startswith("filter_date_"))

# 📌 Register Currency Filter
router.callback_query.register(filter_currency, F.data == "filter_currency")
router.callback_query.register(filter_currency_process, F.data.startswith("filter_currency_"))

# 📌 Register Status Filter
router.callback_query.register(filter_status, F.data == "filter_status")
router.callback_query.register(filter_status_process, F.data.startswith("filter_status_"))








# B2B
## menu
from qarz_b2b.b2b_menu import b2b_menu
router.callback_query(F.data.startswith("b2b"))(b2b_menu)
## company registration
from qarz_b2b.qarz_registration.company_name import process_company_name
router.message(StateFilter(CompanyRegistration.company_name))(process_company_name)
## company phone
from qarz_b2b.qarz_registration.company_phone import process_company_phone
router.message(StateFilter(CompanyRegistration.company_phone))(process_company_phone)


async def qarz_main():
    await init_db()  # Initialize the database pool before starting the bot
    dp.include_router(router)  # Register the router with the dispatcher
    print("Bot started.")
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(qarz_main())