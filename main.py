from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram import Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import asyncio
import re
from config import API_TOKEN, BOT_USERNAME, max_user_per_page
from datetime import datetime

# API_TOKEN = '7314896845:AAE4AXQdXTaeaN-BfegtS2EbzHKi7U68OOw'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_position = State()
    waiting_for_birthdate = State()
    waiting_for_new_name = State()
    waiting_for_new_phone = State()
    waiting_for_new_position = State()
    waiting_for_new_birthdate = State()
    main_menu_message_id = State()

class CompanySettingsStates(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_new_company_name = State()
    waiting_for_new_group_name = State()

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userID INTEGER NOT NULL UNIQUE,
                        userToken VARCHAR(5) NOT NULL UNIQUE,
                        fullname VARCHAR(255) DEFAULT NULL,
                        phone_number VARCHAR(13) DEFAULT NULL,
                        position VARCHAR(255) DEFAULT NULL,
                        birthdate DATE DEFAULT NULL,
                        role VARCHAR(8) NOT NULL DEFAULT 'Boss',
                        company_id INTEGER DEFAULT 0 REFERENCES company(id),
                        group_id INTEGER DEFAULT NULL REFERENCES user_group(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS company (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name VARCHAR(255) NOT NULL UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_group (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name VARCHAR(255) NOT NULL,
                        company_id INTEGER NOT NULL REFERENCES company(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS task_list (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_title VARCHAR(255) NOT NULL,
                        task_description TEXT NOT NULL,
                        start_date DATE NOT NULL,
                        due_date DATE NOT NULL,
                        priority VARCHAR(10) NOT NULL DEFAULT 'Low',
                        status VARCHAR(10) NOT NULL DEFAULT 'Not started',
                        task_owner_id INTEGER NOT NULL REFERENCES user(id),
                        task_assignee_id INTEGER NOT NULL REFERENCES user(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP DEFAULT NULL,
                        paused_at TIMESTAMP DEFAULT NULL,
                        continued_at TIMESTAMP DEFAULT NULL,
                        finished_at TIMESTAMP DEFAULT NULL)''')
    conn.commit()
    conn.close()

init_db()


async def ask_for_next_missing_field(message: types.Message, state: FSMContext):
    userID = message.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id, role FROM user WHERE userID = ?", (userID,))
        user = cursor.fetchone()

    if not user:
        await message.answer("Пользователь не найден. Пожалуйста, начните регистрацию заново.")
        return False

    fullname, phone_number, position, birthdate, company_id, role = user

    # Check each field and prompt the user if it is missing
    if not fullname:
        await message.answer("Напишите полное имя:")
        await state.set_state(RegistrationStates.waiting_for_fullname)
        return False
    elif not phone_number or phone_number == "NULL":
        await ask_for_phone_number(message, state)
        return False
    elif not position:
        await message.answer("Введите вашу должность:")
        await state.set_state(RegistrationStates.waiting_for_position)
        return False
    elif not birthdate:
        await message.answer("Введите вашу дату рождения в формате (дд.мм.гггг):")
        await state.set_state(RegistrationStates.waiting_for_birthdate)
        return False
    elif not company_id:
        await message.answer("Пожалуйста, введите название вашей компании для создания:")
        await state.set_state(CompanySettingsStates.waiting_for_company_name)
        return False

    # Clear the state if all fields are complete
    await state.clear()

    return True


async def generate_user_token():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(userToken) FROM user")
        max_token = cursor.fetchone()[0]

        if max_token is None:
            new_token = 'AA002'
        else:
            while True:
                new_token_number = int(max_token[2:]) + 1
                new_token = f"AA{new_token_number:03d}"
                if new_token not in ['AA001', 'AA007', 'AA077']:
                    break
                max_token = new_token

        return new_token

@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message, state: FSMContext):
    userID = message.from_user.id

    # Extract arguments manually from the /start command
    args = message.text.split(" ", 1)
    company_id = None
    group_id = None

    # If there are any arguments after /start, parse them
    if len(args) > 1 and args[1]:
        try:
            params = dict(param.split('=') for param in args[1].split('&') if '=' in param)
            company_id = params.get('start')
            group_id = params.get('group')
        except Exception as e:
            print(f"Error parsing arguments: {e}")

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID = ?", (userID,))
        user = cursor.fetchone()
        userToken = await generate_user_token()

        if user:
            role, existing_company_id, existing_group_id = user

            complete = await ask_for_next_missing_field(message, state)

            if complete:
                if role == 'Boss' and not existing_company_id:
                    await ask_for_company(message, state)
                else:
                    await message.answer("Вы уже зарегистрированы и присоединены к компании. Добро пожаловать!")
                    await main_menu(message, state, role=role)
        else:
            if company_id:
                # Convert company_id and group_id to integers
                try:
                    company_id = int(company_id)
                    if group_id:
                        group_id = int(group_id)
                except ValueError:
                    await message.reply("Некорректная ссылка. Пожалуйста, попробуйте снова.")
                    return

                # Assign the role "Worker" when joining through a referral link
                cursor.execute("INSERT INTO user (userID, userToken, role, company_id, group_id) VALUES (?, ?, ?, ?, ?)",
                               (userID, userToken, "Worker", company_id, group_id))
                conn.commit()
                company_name = cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,)).fetchone()[0]
                
                complete = await ask_for_next_missing_field(message, state)
                if complete:
                    await message.reply(f"Добро пожаловать! Вы зарегистрированы как сотрудник компании {company_name} через реферальную ссылку.")
                    await main_menu(message, state, role="Worker")
            else:
                # If the user didn't join via a referral link, assign the role "Boss"
                cursor.execute("INSERT INTO user (userID, userToken, role) VALUES (?, ?, ?)", (userID, userToken, "Boss"))
                conn.commit()
                await message.reply("Добро пожаловать! Пожалуйста, давайте приступим к процессу регистрации как руководитель компании.")
                
                # Start the registration process for the user
            await ask_for_next_missing_field(message, state)

async def ask_for_phone_number(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer("Отправьте номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже для отправки контакта.", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(StateFilter(RegistrationStates.waiting_for_phone))
async def process_phone(message: types.Message, state: FSMContext):
    # Get the phone number from the message (contact or text)
    phone_number = message.contact.phone_number if message.contact else message.text
    
    # Normalize the phone number: remove '+' if it exists
    normalized_phone_number = phone_number.lstrip('+')

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET phone_number=? WHERE userID=?", (normalized_phone_number, message.from_user.id))
            conn.commit()
        
        await message.answer("Телефон успешно сохранен.", reply_markup=ReplyKeyboardRemove())
        await ask_for_next_missing_field(message, state)
    else:
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX.")
        return

    

@router.message(StateFilter(RegistrationStates.waiting_for_fullname))
async def process_fullname(message: types.Message, state: FSMContext):
    fullname = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET fullname=? WHERE userID=?", (fullname, message.from_user.id))
        conn.commit()
    
    await ask_for_next_missing_field(message, state)

@router.message(StateFilter(RegistrationStates.waiting_for_position))
async def process_position(message: types.Message, state: FSMContext):
    position = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET position=? WHERE userID=?", (position, message.from_user.id))
        conn.commit()
    
    await ask_for_next_missing_field(message, state)

@router.message(StateFilter(RegistrationStates.waiting_for_birthdate))
async def process_birthdate(message: types.Message, state: FSMContext):
    birthdate = message.text
    
    try:
        date_obj = datetime.strptime(birthdate, '%d.%m.%Y')
        if date_obj.year < 1920 or date_obj.year > 2020:
            raise ValueError("Год должен быть между 1920 и 2020")
    except ValueError as e:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг.")
        return
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET birthdate=? WHERE userID=?", (birthdate, message.from_user.id))
        conn.commit()

    # Clear the state after the last required field is entered
    complete = await ask_for_next_missing_field(message, state)
    
    if complete:
        # Fetch the role of the user from the database
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM user WHERE userID=?", (message.from_user.id,))
            role = cursor.fetchone()[0]

        await message.answer("Регистрация завершена. Добро пожаловать!")
        await main_menu(message, state, role)

async def ask_for_company(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите название вашей компании для создания:")
    await state.set_state(CompanySettingsStates.waiting_for_company_name)

@router.message(StateFilter(CompanySettingsStates.waiting_for_company_name))
async def process_company(message: types.Message, state: FSMContext):
    company_name = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM company WHERE company_name=?", (company_name,))
        company = cursor.fetchone()

        cursor.execute("SELECT role FROM user WHERE userID=?", (message.from_user.id, ))
        role = cursor.fetchone()[0]
        
        if company:
            await message.answer(f"Компания '{company_name}' уже существует. Пожалуйста, введите другое название. Если вы не являетесь администратором компании, обратитесь к администратору.")
            return
        else:
            cursor.execute("INSERT INTO company (company_name) VALUES (?)", (company_name,))
            company_id = cursor.lastrowid
            
            cursor.execute("UPDATE user SET company_id=? WHERE userID=?", (company_id, message.from_user.id))
            conn.commit()

            await message.answer(f"Компания '{company_name}' успешно создана.\nРегистрация завершена. Добро пожаловать!")
            await main_menu(message, state, role)

    await state.clear()

async def is_valid_menu_message(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    # If the message ID does not match the stored one, show an alert and return False
    if main_menu_message_id != callback_query.message.message_id:
        try:
            await callback_query.answer("Эта кнопка не активна.", show_alert=True)
        except Exception as e:
            await callback_query.answer(f"Проблема с кнопкой: {e}", show_alert=True)
        return False
    return True

async def main_menu(message: types.Message, state: FSMContext, role):
    keyboard = None
    if role == 'Boss':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings"), InlineKeyboardButton(text="Настройки компании", callback_data="company_settings")],
            ]
        )
    elif role == "Manager":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings")],
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings")],
            ]
        )

    # Retrieve the existing main menu message ID from the state
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id:
        # Try to edit the existing message if the ID is available
        try:
            await bot.edit_message_text("Главное меню", chat_id=message.chat.id, message_id=main_menu_message_id, reply_markup=keyboard)
        except Exception as e:
            # If editing fails (e.g., the message doesn't exist), send a new one and update the state
            sent_message = await message.answer("Главное меню", reply_markup=keyboard)
            await state.update_data(main_menu_message_id=sent_message.message_id)
    else:
        # If no previous main menu message ID is stored, send a new main menu
        sent_message = await message.answer("Главное меню", reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)


@router.callback_query(lambda call: call.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM user WHERE userID=?", (callback_query.from_user.id,))
            role = cursor.fetchone()[0]
            try:
                await callback_query.message.delete()
            except Exception as e:
                pass
            await main_menu(callback_query.message, state, role=role)

@router.callback_query(lambda call: call.data == "user_settings")
async def show_user_settings(callback_query: types.CallbackQuery):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Изменить данные пользователя", callback_data="show_change_data_menu")],
                [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
            ]
        )
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id FROM user WHERE userID=?", (callback_query.from_user.id,))
            user = cursor.fetchone()
            fullname, phone_number, position, birthdate, company_id = user
            cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,))
            company_name = cursor.fetchone()[0]
            user_data_message = f"Ваши данные:\nФИО: {fullname}\nТелефон: {phone_number}\nДолжность: {position}\nДата рождения: {birthdate}\nВаша компания: {company_name}"
            await callback_query.message.edit_text(user_data_message, reply_markup=keyboard)

async def show_user_settings_for_message(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить данные пользователя", callback_data="show_change_data_menu")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
        ]
    )
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id FROM user WHERE userID=?", (message.from_user.id,))
        user = cursor.fetchone()
        fullname, phone_number, position, birthdate, company_id = user
        cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        user_data_message = f"Ваши данные:\nФИО: {fullname}\nТелефон: {phone_number}\nДолжность: {position}\nДата рождения: {birthdate}\nВаша компания: {company_name}"
    
    send_message = await message.answer(user_data_message, reply_markup=keyboard)
    await state.update_data(main_menu_message_id=send_message.message_id)

@router.callback_query(lambda call: call.data == "show_change_data_menu")
async def show_change_data_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить ФИО", callback_data="change_fullname")],
            [InlineKeyboardButton(text="Изменить телефон", callback_data="change_phone")],
            [InlineKeyboardButton(text="Изменить должность", callback_data="change_position")],
            [InlineKeyboardButton(text="Изменить дату рождения", callback_data="change_birthdate")],
            [InlineKeyboardButton(text="Назад", callback_data="user_settings")],
        ]
    )
    await callback_query.message.edit_text("Выберите, что хотите изменить:", reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "change_fullname")
async def change_fullname(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_change_data_menu")],
        ]
    )
    await callback_query.message.edit_text("Введите новое ФИО:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_new_name)

@router.message(StateFilter(RegistrationStates.waiting_for_new_name))
async def process_new_name(message: types.Message, state: FSMContext):
    fullname = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET fullname=? WHERE userID=?", (fullname, message.from_user.id))
        conn.commit()
    
    await message.answer("ФИО успешно изменено.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)  # Correct function to show user settings

@router.callback_query(lambda call: call.data == "change_phone")
async def change_phone(callback_query: types.CallbackQuery, state: FSMContext):
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback_query.message.answer("Отправьте номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже для отправки контакта:", reply_markup=reply_keyboard)
    
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_change_data_menu")],
        ]
    )
    await callback_query.message.edit_text("Введите новый номер телефона или отправьте контакт:", reply_markup=inline_keyboard)

    await state.set_state(RegistrationStates.waiting_for_new_phone)


@router.message(StateFilter(RegistrationStates.waiting_for_new_phone))
async def process_new_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    
    # Normalize the phone number: remove '+' if it exists
    normalized_phone_number = phone_number.lstrip('+')

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET phone_number=? WHERE userID=?", (normalized_phone_number, message.from_user.id))
            conn.commit()
        
        await message.answer("Телефон успешно сохранен.", reply_markup=ReplyKeyboardRemove())
        await show_user_settings_for_message(message, state)
    else:
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX.")
        return

@router.callback_query(lambda call: call.data == "change_position")
async def change_position(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_change_data_menu")],
        ]
    )
    await callback_query.message.edit_text("Введите новую должность:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_new_position)

@router.message(StateFilter(RegistrationStates.waiting_for_new_position))
async def process_new_position(message: types.Message, state: FSMContext):
    position = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET position=? WHERE userID=?", (position, message.from_user.id))
        conn.commit()
    
    await message.answer("Должность успешно изменена.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)

@router.callback_query(lambda call: call.data == "change_birthdate")
async def change_birthdate(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_change_data_menu")],
        ]
    )
    await callback_query.message.edit_text("Введите новую дату рождения в формате (дд.мм.гггг):", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_new_birthdate)

@router.message(StateFilter(RegistrationStates.waiting_for_new_birthdate))
async def process_new_birthdate(message: types.Message, state: FSMContext):
    birthdate = message.text
    
    try:
        date_obj = datetime.strptime(birthdate, '%d.%m.%Y')
        if date_obj.year < 1920 or date_obj.year > 2020:
            raise ValueError("Год должен быть между 1920 и 2020")
    except ValueError as e:
        await message.answer(f"Некорректный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг.")
        return
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET birthdate=? WHERE userID=?", (birthdate, message.from_user.id))
        conn.commit()

    await message.answer("Дата рождения успешно изменена.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)

@router.callback_query(lambda call: call.data == "company_settings")
async def show_company_settings(callback_query: types.CallbackQuery, state: FSMContext):
    userID = callback_query.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM user WHERE userID=?", (userID,))
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        workerCount = cursor.execute("SELECT COUNT(*) FROM user WHERE company_id=?", (company_id,)).fetchone()[0]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees")],
            [InlineKeyboardButton(text="Управлять отделами", callback_data="manage_groups")],
            [InlineKeyboardButton(text="Изменить название компании", callback_data="change_company_name")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
        ]
    )
    await callback_query.message.edit_text(f"Здравствуйте, администратор компании!\nВаша компания {company_name}.\nЧисло сотрудников: {workerCount}\n\nХотите что-нибудь изменить?", reply_markup=keyboard)

async def show_company_settings_msg(message: types.Message):
    userID = message.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM user WHERE userID=?", (userID,))
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        workerCount = cursor.execute("SELECT COUNT(*) FROM user WHERE company_id=?", (company_id,)).fetchone()[0]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees")],
            [InlineKeyboardButton(text="Управлять отделами", callback_data="manage_groups")],
            [InlineKeyboardButton(text="Изменить название компании", callback_data="change_company_name")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
        ]
    )
    await message.answer(f"Здравствуйте, администратор компании!\nВаша компания {company_name}.\nЧисло сотрудников: {workerCount}\n\nХотите что-нибудь изменить?", reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "change_company_name")
async def change_company_name(callback_query: types.CallbackQuery, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="company_settings")],
            ]
        )
        await callback_query.message.edit_text("Введите новое название компании:", reply_markup=keyboard)
        await state.set_state(CompanySettingsStates.waiting_for_new_company_name)

@router.message(StateFilter(CompanySettingsStates.waiting_for_new_company_name))
async def process_new_company_name(message: types.Message, state: FSMContext):
    new_company_name = message.text

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM user WHERE userID=?", (message.from_user.id,))
        company_id = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM company WHERE id=?", (company_id,))
        company = cursor.fetchone()

        # Check if the new company name already exists
        if new_company_name == company[1]:
            await message.answer(f"Компания '{new_company_name}' уже существует. Пожалуйста, введите другое название. Если вы не являетесь администратором компании, обратитесь к администратору.")
            return
        else:
            cursor.execute("UPDATE company SET company_name = ? WHERE id = ?", (new_company_name, company_id))
            conn.commit()  # Commit the changes

            await message.answer("Название компании успешно изменено.")
            await show_company_settings_msg(message)  # Call the main menu to refresh buttons properly

    await state.clear()

@router.callback_query(lambda call: call.data.startswith("list_of_employees"))
async def show_list_of_employees(callback_query: types.CallbackQuery, state: FSMContext):
        # Check if the callback data contains a page number
        if "page" in callback_query.data:
            page = int(callback_query.data.split("_")[-1])
        else:
            page = 1  # Default to page 1 if it's the first time

        offset = (page - 1) * max_user_per_page

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_id FROM user WHERE userID=?", (callback_query.from_user.id,))
            company_id = cursor.fetchone()[0]
            cursor.execute("SELECT id, userID, userToken, fullname FROM user WHERE company_id=? LIMIT ? OFFSET ?", (company_id, max_user_per_page, offset))
            employees = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM user WHERE company_id=?", (company_id,))
            total_employees = cursor.fetchone()[0]

        # Calculate total pages
        total_pages = (total_employees + max_user_per_page - 1) // max_user_per_page

        # Build the inline keyboard with employee buttons and pagination
        employee_buttons = [
            [
                InlineKeyboardButton(
                    text=f"{employee[2]} {employee[3]} - Это вы" if employee[1] == callback_query.from_user.id else f"{employee[2]} {employee[3]}",
                    callback_data="user_settings" if employee[1] == callback_query.from_user.id else f"employee_{employee[0]}"
                )
            ]
            for employee in employees
        ]

        # Add pagination buttons if necessary
        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"list_of_employees_page_{page - 1}"))
        if page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"list_of_employees_page_{page + 1}"))

        if navigation_buttons:
            employee_buttons.append(navigation_buttons)  # Add pagination buttons
        employee_buttons.append([InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=employee_buttons)

        await callback_query.message.edit_text(f"Список всех сотрудников (Страница {page}/{total_pages}):", reply_markup=keyboard)


@router.callback_query(lambda call: call.data == "referral_links")
async def show_referral_links(callback_query: types.CallbackQuery, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")]
            ]
        )
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, company_id FROM user WHERE userID=?", (callback_query.from_user.id,))
            role, company_id = cursor.fetchone()
            cursor.execute("SELECT * FROM company WHERE id=?", (company_id,))
            company = cursor.fetchone()
            cursor.execute("SELECT * FROM user_group WHERE company_id=?", (company_id,))
            user_groups = cursor.fetchall()

            # Initialize the message with the company referral link
            message = f"Ваша реферальная ссылка для приглашения в компанию '{company[1]}':\n\n"

            # Iterate through user groups and add each group's referral link
            if user_groups:
                for user_group in user_groups:
                    group_id, group_name, _ = user_group
                    referal_link_group = f"https://t.me/{BOT_USERNAME}?start={company_id}&group={group_id}"
                    message += f"Для отдела '{group_name}':\n {referal_link_group}\n\n"
            else:
                message += f"На вашей компании нет отделов."
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Создать отдел", callback_data="create_group")],
                        [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")]
                    ]
                )

            # Edit the message with the accumulated referral links
            await callback_query.message.edit_text(message, reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "manage_groups")
async def manage_groups(callback_query: types.CallbackQuery, state: FSMContext):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_id FROM user WHERE userID=?", (callback_query.from_user.id,))
            company_id = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM user_group WHERE company_id=?", (company_id,))
            user_groups = cursor.fetchall()
        if user_groups:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Создать отдел", callback_data="create_group")],
                    [InlineKeyboardButton(text="Изменить наименование отдела", callback_data="change_group_name")],
                    [InlineKeyboardButton(text="Удалить отдел", callback_data="delete_group")],
                    [InlineKeyboardButton(text="Назад", callback_data="company_settings")],
                ]
            )
            groups_list = "\n".join([f"{group[1]} - {group[2]} сотрудников" for group in user_groups])
            await callback_query.message.edit_text(f"Список отделов:\n{groups_list}", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Создать отдел", callback_data="create_group")],
                    [InlineKeyboardButton(text="Назад", callback_data="company_settings")],
                ]
            )
            await callback_query.message.edit_text("У вас пока нет отделов. Создайте новый отдел.", reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "create_group")
async def create_group(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="manage_groups")],
        ]
    )
    await callback_query.message.edit_text("Введите название нового отдела:", reply_markup=keyboard)
    await state.set_state(CompanySettingsStates.waiting_for_new_group_name)

@router.message(StateFilter(CompanySettingsStates.waiting_for_new_group_name))
async def process_new_group_name(message: types.Message, state: FSMContext):
    new_group_name = message.text

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id FROM user WHERE userID=?", (message.from_user.id,))
        role, company_id = cursor.fetchone()

        cursor.execute("INSERT INTO user_group (company_id, group_name) VALUES (?, ?)", (company_id, new_group_name))
        conn.commit()

    await message.answer("Отдел успешно создан.")
    await state.update_data(main_menu_message_id=0)
    await main_menu(message, state, role)  # Call the main menu to refresh buttons properly

@router.callback_query(lambda call: call.data == "task_list")
async def show_task_list(callback_query: types.CallbackQuery, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")]
            ]
        )
        await callback_query.message.edit_text("Вы выбрали: Список задач.", reply_markup=keyboard)
        
async def notify_user_on_reload():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT userID FROM user")
        user = cursor.fetchall()
        for user in user:
            try:
                await bot.send_message(user[0], "Бот был перезагружен. Пожалуйста, напишите команду /start, чтобы продолжить.")
            except Exception as e:
                print(f"Error sending message to user {user[0]}: {e}")

dp.include_router(router)

async def main():
    await notify_user_on_reload()

    await dp.start_polling(bot)

if __name__ == '__main__':
    init_db()
    asyncio.run(main())
