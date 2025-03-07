from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    lang = State()
    fullname = State()
    phone_number = State()
    birthdate = State()
    approve_rules = State()
    waiting_for_approve = State()
    waiting_for_approve_type = State()

class GetDebtCreation(StatesGroup):
    getdebt_creditor = State()
    getdebt_creditor_phone = State()
    getdebt_amount = State()
    getdebt_currency = State()
    getdebt_loan_date = State()
    getdebt_due_date = State()
    getdebt_amounts = State()
    getdebt_comment = State()

class GiveDebtCreation(StatesGroup):
    givedebt_debtor = State()
    givedebt_debtor_phone = State()
    givedebt_amount = State()
    givedebt_currency = State()
    givedebt_loan_date = State()
    givedebt_due_date = State()
    givedebt_amounts = State()
    givedebt_comment = State()

class RejectionStates(StatesGroup):
    rejected_id = State()
    rejected_type = State()
    reason = State()

class MessageStates(StatesGroup):
    main_message_id = State()

class EnterAmountState(StatesGroup):
    amount_debt_id = State()
    entered_amount = State()

class ChangeUserData(StatesGroup):
    user_name = State()
    user_phone = State()
    user_birthday = State()

class ChangeTypeUser(StatesGroup):
    user_type = State()

class CompanyRegistration(StatesGroup):
    company_name = State()
    company_phone = State()

class LendingState(StatesGroup):
    lending_creation = State()
    clending_fullamount = State()
    clending_item_name = State()
    clending_item_measure = State()
    clending_item_quantity = State()
    clending_item_price = State()
    clending_borrower = State()
    lending_get = State()