from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    fullname = State()
    phone_number = State()
    birthdate = State()

class CompanyCreation(StatesGroup):
    company_name = State()

class DepartmentCreation(StatesGroup):
    department_name = State()

class ProjectCreation(StatesGroup):
    project_name = State()

class MainMessage(StatesGroup):
    main_menu_message_id = State()

class UserChanges(StatesGroup):
    fullname = State()
    phone_number = State()
    birthdate = State()

class CompanyChanges(StatesGroup):
    company_name = State()

class DepartmentChanges(StatesGroup):
    department_id = State()
    department_name = State()