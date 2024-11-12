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

class TaskCreation(StatesGroup):
    project_id = State()
    task_title = State()
    task_description = State()
    start_date = State()
    due_date = State()
    task_assignee_phone = State()
    task_assignee_id = State()
    priority = State()
    task_confirm = State()

class TaskChanges(StatesGroup):
    task_id = State()
    task_title = State()
    task_description = State()
    new_start_date = State()
    new_due_date = State()
    priority = State()

class DraftChanges(StatesGroup):
    draft_id = State()
    draft_title = State()
    draft_description = State()
    draft_start_date = State()
    draft_due_date = State()
    draft_assignee_id = State()
    draft_priority = State()
    draft_confirm = State()