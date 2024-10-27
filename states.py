from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    fullname = State()
    phone_number = State()
    birthdate = State()

class CompanyCreation(StatesGroup):
    company_name = State()

class DepartmentCreation(StatesGroup):
    department_name = State()

class MainMessage(StatesGroup):
    main_menu_message_id = State()