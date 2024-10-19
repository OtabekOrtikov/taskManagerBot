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

from annotated_types import LowerCase
from config import API_TOKEN, BOT_USERNAME, max_user_per_page, max_task_per_page
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

class TaskCreationStates(StatesGroup):
    assignee_id = State()
    waiting_for_task_title = State()
    waiting_for_task_description = State()
    waiting_for_task_start_date = State()
    waiting_for_task_due_date = State()
    waiting_for_task_priority = State()
    waiting_for_task_assignee = State()
    waiting_for_task_confirmation = State()

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS task (
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
            # Assuming that the format is "1_group=1", split it
            params = args[1].split('_')
            company_id = params[0]
            if len(params) > 1:
                group_id = params[1].split('=')[1]  # Extract group_id from "group=1"

            print(f"Parsed company_id: {company_id}, group_id: {group_id}, user_id: {userID}")  # Debugging info
        except Exception as e:
            print(f"Error parsing arguments: {e}")
            await message.reply("Ошибка в параметрах ссылки. Пожалуйста, проверьте правильность ссылки.")
            return

    # Ensure company_id and group_id are integers
    if company_id:
        try:
            company_id = int(company_id)
        except ValueError:
            await message.reply("Некорректный идентификатор компании. Попробуйте снова.")
            return

    if group_id:
        try:
            group_id = int(group_id)
        except ValueError:
            await message.reply("Некорректный идентификатор отдела. Попробуйте снова.")
            return

    # Check if the user already exists in the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID = ?", (userID,))
        user = cursor.fetchone()
        userToken = await generate_user_token()

        if user:
            # If user already exists in the database
            role, existing_company_id, existing_group_id = user
            complete = await ask_for_next_missing_field(message, state)

            if complete:
                if role == 'Boss' and not existing_company_id:
                    await ask_for_company(message, state)
                else:
                    await message.answer("Вы уже зарегистрированы и присоединены к компании. Добро пожаловать!")
                    await main_menu(message, state, role=role)
        else:
            # Handle users joining with a referral link
            if company_id and group_id:
                # Check if there are already users in the company/group
                cursor.execute("SELECT COUNT(*) FROM user WHERE company_id = ? AND group_id = ?", (company_id, group_id))
                user_count = cursor.fetchone()[0]

                # Assign role based on whether the user is the first to join
                if user_count == 0:
                    role = "Manager"
                    await message.reply(f"Добро пожаловать! Вы зарегистрированы как менеджер компании.")
                else:
                    role = "Worker"
                    await message.reply(f"Добро пожаловать! Вы зарегистрированы как сотрудник компании.")

                # Insert the user with the appropriate role
                cursor.execute("INSERT INTO user (userID, userToken, role, company_id, group_id) VALUES (?, ?, ?, ?, ?)",
                               (userID, userToken, role, company_id, group_id))
                conn.commit()

                company_name = cursor.execute("SELECT company_name FROM company WHERE id=?", (company_id,)).fetchone()[0]

                complete = await ask_for_next_missing_field(message, state)
                if complete:
                    await main_menu(message, state, role=role)
            else:
                # Handle users joining without a referral link (assign role "Boss")
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
        # Fetch specific user data from the database
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userID, userToken, fullname, phone_number, position, birthdate, role, company_id, group_id FROM user WHERE userID=?", (message.from_user.id,))
            user_data = cursor.fetchone()
            userID, userToken, fullname, phone_number, position, birthdate, role, company_id, group_id = user_data

            cursor.execute("SELECT group_name FROM user_group WHERE id=?", (group_id,))
            group_name = cursor.fetchone()[0]

            cursor.execute("SELECT userID FROM user WHERE role='Boss' AND company_id=?", (company_id,))
            boss_id = cursor.fetchone()[0]

        await message.answer("Регистрация завершена. Добро пожаловать!")
        
        # Notify the Boss about the new employee
        await bot.send_message(boss_id, f"Новый сотрудник успешно зарегистрирован.\n\nЕго данные:\nПользовательский токен: {userToken}\nИмя: {fullname}\nДолжность: {position}\nДата рождения: {birthdate}\nТелефон: +{phone_number}\nОтдел: {group_name}")
        
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
                [InlineKeyboardButton(text="Список задач", callback_data="show_task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings"), InlineKeyboardButton(text="Настройки компании", callback_data="company_settings")],
            ]
        )
    elif role == "Manager":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="show_task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings")],
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="show_task_list")],
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
        # Get the current user's role and company_id
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID=?", (callback_query.from_user.id,))
        user_info = cursor.fetchone()
        role, company_id, group_id = user_info

        if role == "Boss":
            # Boss can see all employees across the company, including their group names
            cursor.execute("""
                SELECT u.id, u.userID, u.userToken, u.fullname, u.role, g.group_name
                FROM user u
                LEFT JOIN user_group g ON u.group_id = g.id
                WHERE u.company_id = ?""", (company_id,))
            employees = cursor.fetchall()
        elif role == "Manager":
            # Manager can only see employees in their group, excluding the manager themselves
            cursor.execute("""
                SELECT u.id, u.userID, u.userToken, u.fullname, u.role
                FROM user u
                WHERE u.company_id = ? AND u.group_id = ?""", (company_id, group_id))
            employees = cursor.fetchall()

    # Filter out the current user and the boss from the employees list
    filtered_employees = [
        employee for employee in employees if employee[1] != callback_query.from_user.id and employee[4] != 'Boss'
    ]

    # Calculate total employees after filtering
    total_employees = len(filtered_employees)

    # Apply pagination after filtering
    paginated_employees = filtered_employees[offset:offset + max_user_per_page]

    # Calculate total pages
    total_pages = (total_employees + max_user_per_page - 1) // max_user_per_page

    # Build the inline keyboard with employee buttons and pagination
    employee_buttons = []
    for employee in paginated_employees:
        employee_id, employee_userID, employee_userToken, employee_fullname = employee[:4]

        # For Boss, show userToken, fullname, and group_name; for Manager, just userToken and fullname
        if role == "Boss":
            group_name = employee[5] if employee[5] else "Без отдела"
            employee_text = f"{employee_userToken} {employee_fullname} - {group_name}"
        else:
            employee_text = f"{employee_userToken} {employee_fullname}"

        employee_buttons.append([InlineKeyboardButton(text=employee_text, callback_data=f"employee_{employee_id}")])

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

    if total_employees == 0:
        await callback_query.message.edit_text("В вашем отделе пока нет сотрудников кроме вас.", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(f"Список сотрудников (Страница {page}/{total_pages}):", reply_markup=keyboard)


@router.callback_query(lambda call: call.data == "referral_links")
async def show_referral_links(callback_query: types.CallbackQuery, state: FSMContext):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID=?", (callback_query.from_user.id,))
        role, company_id, group_id = cursor.fetchone()
        cursor.execute("SELECT * FROM company WHERE id=?", (company_id,))
        company = cursor.fetchone()
        cursor.execute("SELECT * FROM user_group where company_id=?", (company_id,))
        groups = cursor.fetchall()
        
        if group_id:
            cursor.execute("SELECT group_name FROM user_group WHERE id=?", (group_id,))
            user_group_name = cursor.fetchone()[0]

        if role == "Boss":
            # Referral link for the entire company
            message = f"Реферальные ссылки для компании '{company[1]}':\n\n"

            if groups:
                for group in groups:
                    group_id, group_name = group[0], group[1]
                    referral_link_group = f"https://t.me/{BOT_USERNAME}?start={company_id}_group={group_id}"
                    message += f"Отдел '{group_name}':\n{referral_link_group}\n\n"
            else:
                message += "Ваша компания пока не имеет отделов."
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")]
                ]
            )
        else:
            # Referral link for a specific group
            referral_link_group = f"https://t.me/{BOT_USERNAME}?start={company_id}_group={group_id}"
            message = f"Скопируйте реферальную ссылку для отдела компании '{user_group_name}' и отправьте её другим:\n\n{referral_link_group}"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Скопировать ссылку на отдел", url=referral_link_group)],
                    [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")]
                ]
            )

    # Send or edit the message with the referral link
    await callback_query.message.edit_text(message, reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith("employee_"))
async def employee_details_handler(callback_query: types.CallbackQuery):
    # Extract the employee_id from the callback data
    employee_id = int(callback_query.data.split("_")[1])

    # Connect to the database to fetch the employee details
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT userToken, fullname, phone_number, position, birthdate, role, group_id FROM user WHERE id=?", (employee_id,))
        employee_data = cursor.fetchone()
        cursor.execute("SELECT role FROM user WHERE userID=?", (callback_query.from_user.id,))
        handlerRole = cursor.fetchone()[0]

    if employee_data:
        userToken, fullname, phone_number, position, birthdate, role, group_id = employee_data

        # Fetch group name if group_id is present
        cursor.execute("SELECT group_name FROM user_group WHERE id=?", (group_id,))
        group_name = cursor.fetchone()[0] if group_id else "No group"

        # Create a detailed message about the employee
        employee_details = (
            f"Информация о сотруднике:\n"
            f"Токен: {userToken}\n"
            f"Имя: {fullname}\n"
            f"Телефон: {phone_number}\n"
            f"Должность: {position}\n"
            f"Дата рождения: {birthdate}\n"
            f"Отдел: {group_name}\n"
            f"Текущая роль: {'Администратор отдела' if role == 'Manager' else 'Сотрудник'}"
        )

        # Define the role change button
        inline_keyboard = []

        inline_keyboard.append([InlineKeyboardButton(text="Создать задачу", callback_data=f"create_task_user_{employee_id}")])
        inline_keyboard.append([InlineKeyboardButton(text="Список задач сотрудника", callback_data=f"show_task_list_user_{employee_id}")])

        if handlerRole == "Boss":
            if role == "Manager":
                inline_keyboard.append([InlineKeyboardButton(text="Сделать обычным сотрудником", callback_data=f"confirm_change_role_{employee_id}_Worker")])
            else:
                inline_keyboard.append([InlineKeyboardButton(text="Сделать администратором отдела", callback_data=f"confirm_change_role_{employee_id}_Manager")])

        inline_keyboard.append([InlineKeyboardButton(text="Назад к списку сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")])
        
        # Send the details to the user with role change button
        await callback_query.message.edit_text(employee_details, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
    else:
        await callback_query.answer("Сотрудник не найден.", show_alert=True)

@router.callback_query(lambda call: call.data.startswith("confirm_change_role_"))
async def confirm_role_change(callback_query: types.CallbackQuery):
    # Extract the employee_id and new_role from the callback data
    data_parts = callback_query.data.split("_")
    
    # Ensure that the data is correctly split (there should be 4 parts)
    if len(data_parts) != 5:
        await callback_query.answer(f"Ошибка при обработке запроса. {data_parts[0]} {data_parts[1]} {data_parts[2]} {data_parts[3]} {data_parts[4]} {len(data_parts)}", show_alert=True)
        return

    _, _, _, employee_id, new_role = data_parts  # Splitting into 4 parts

    # Ask for confirmation before changing the role
    await callback_query.message.edit_text(
        f"Вы уверены, что хотите изменить роль этого сотрудника на '{'Администратор отдела' if new_role == 'Manager' else 'Сотрудник'}'?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data=f"change_role_{employee_id}_{new_role}")],
                [InlineKeyboardButton(text="Нет", callback_data=f"employee_{employee_id}")]
            ]
        )
    )

@router.callback_query(lambda call: call.data.startswith("change_role_"))
async def change_employee_role(callback_query: types.CallbackQuery, state: FSMContext):
    # Extract the employee_id and the new role from the callback data
    _,_, employee_id, new_role = callback_query.data.split("_")

    # Connect to the database to update the employee's role
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET role=? WHERE id=?", (new_role, employee_id))
        conn.commit()

    # Send a success message to the user
    await callback_query.answer(f"Роль сотрудника успешно изменена на {new_role}.", show_alert=True)

    # Show the updated employee details again
    await show_list_of_employees(callback_query, state)

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

@router.callback_query(lambda call: call.data.startswith("show_task_list"))
async def show_task_list(callback_query: types.CallbackQuery, state: FSMContext):
    # Set max groups/tasks per page
    max_group_per_page = 5
    max_task_per_page = 5

    # Check if the callback data contains a page number
    if "page" in callback_query.data:
        page = int(callback_query.data.split("_")[-1])
    else:
        page = 1  # Default to page 1 if it's the first time

    # Set the offset based on the page number
    offset = (page - 1) * max_group_per_page

    await state.set_data({"main_menu_message_id": callback_query.message.message_id})

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID=?", (callback_query.from_user.id,))
        role, company_id, group_id = cursor.fetchone()

        inline_keyboard = []
        message = "Список задач:\n\n"

        if role == "Boss" or role == "Manager":
            inline_keyboard.append([InlineKeyboardButton(text="Создать задачу", callback_data="create_task")])
        
        if role == 'Boss':
            # Fetch the count of groups with tasks for pagination
            cursor.execute("""
                SELECT g.id as group_id, g.group_name, COUNT(t.id) as task_count
                FROM user_group g
                LEFT JOIN user u ON g.id = u.group_id
                LEFT JOIN task t ON t.task_assignee_id = u.id
                WHERE g.company_id = ? AND t.status != 'Finished'
                GROUP BY g.id, g.group_name
                """, (company_id,))
            groups_with_tasks = cursor.fetchall()

            total_groups = len(groups_with_tasks)  # Total number of groups with tasks

            # Apply pagination based on the number of groups
            paginated_groups = groups_with_tasks[offset:offset + max_group_per_page]

            for group in paginated_groups:
                group_id, group_name, task_count = group
                # Add the group and task count as a button
                inline_keyboard.append([InlineKeyboardButton(text=f"{group_name} - {task_count} задач", callback_data=f"show_group_tasks_{group_id}_1")])

            message += f"Всего отделов с задачами: {total_groups}"

        elif role == 'Manager':
            cursor.execute("""
                SELECT t.id as task_id, t.task_title, u.userToken, u.fullname
                FROM task t
                JOIN user u ON t.task_assignee_id = u.id
                WHERE t.status != 'Finished' AND u.company_id = ? AND u.group_id = ?
                LIMIT ? OFFSET ?
            """, (company_id, group_id, max_task_per_page, offset))
            tasks = cursor.fetchall()

            total_tasks = len(tasks)

            message += f"Всего не завершенных задач: {total_tasks}"

            for task in tasks:
                task_id, task_title, userToken, fullname = task
                inline_keyboard.append([InlineKeyboardButton(text=f"{task_title} - {userToken} {fullname}", callback_data=f"task_{task_id}")])
        
        else:
            cursor.execute("SELECT id as user_id FROM user WHERE userID=?", (callback_query.from_user.id,))
            user_id = cursor.fetchone()[0]
            cursor.execute("""
                SELECT id as task_id, task_title, due_date, priority 
                FROM task 
                WHERE task_assignee_id = ?
                LIMIT ? OFFSET ?
                """, (user_id, max_task_per_page, offset))
            tasks = cursor.fetchall()

            total_tasks = len(tasks)

            message += f"Всего не завершенных задач: {total_tasks}"
            for task in tasks:
                task_id, task_title, due_date, priority = task
                inline_keyboard.append([InlineKeyboardButton(text=f"{task_title} - {priority}", callback_data=f"task_{task_id}")])

        # Calculate total pages based on the number of groups for Boss, tasks for others
        if role == 'Boss':
            total_pages = (total_groups + max_group_per_page - 1) // max_group_per_page
        else:
            total_pages = (total_tasks + max_task_per_page - 1) // max_task_per_page

        # Add pagination buttons if necessary
        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"show_task_list_page_{page - 1}"))
        if page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"show_task_list_page_{page + 1}"))

        if navigation_buttons:
            inline_keyboard.append(navigation_buttons)  # Add pagination buttons

        # Add a "Back to main menu" button
        inline_keyboard.append([InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")])
        
        # Create the inline keyboard with task details and navigation buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
        # Update the message to show task list and buttons
        await callback_query.message.edit_text(message, reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith("show_group_tasks"))
async def show_group_tasks(callback_query: types.CallbackQuery):
    # Extract the group_id and page from the callback data
    data_parts = callback_query.data.split("_")
    group_id = int(data_parts[-2])  # group_id is the second-to-last part
    if len(data_parts) > 3 and data_parts[-1].isdigit():
        page = int(data_parts[-1])
    else:
        page = 1  # Default to the first page

    tasks_per_page = 5  # Set the number of tasks to display per page
    offset = (page - 1) * tasks_per_page

    inline_keyboard = []
    inline_keyboard.append([InlineKeyboardButton(text="Создать задачу", callback_data="create_task")])

    # Connect to the database to fetch the tasks for the group
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM user_group WHERE id=?", (group_id,))
        group_name = cursor.fetchone()[0]
        
        # Get total task count for pagination
        cursor.execute("""
            SELECT COUNT(*)
            FROM task t
            JOIN user u ON t.task_assignee_id = u.id
            WHERE u.group_id = ? AND t.status != 'Finished'
        """, (group_id,))
        total_tasks = cursor.fetchone()[0]

        # Fetch the tasks for the current page
        cursor.execute("""
            SELECT t.id as task_id, t.task_title, u.userToken, u.fullname
            FROM task t
            JOIN user u ON t.task_assignee_id = u.id
            WHERE u.group_id = ? AND t.status != 'Finished'
            LIMIT ? OFFSET ?
        """, (group_id, tasks_per_page, offset))
        tasks = cursor.fetchall()

        # Create a message with the tasks for the group
        message = f"Список задач для отдела '{group_name}':\n"
        for task in tasks:
            task_id, task_title, user_token, fullname = task
            inline_keyboard.append([InlineKeyboardButton(text=f"{task_title} - {user_token} {fullname}", callback_data=f"task_{task_id}")])

    # Add pagination buttons
    total_pages = (total_tasks + tasks_per_page - 1) // tasks_per_page
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"show_group_tasks_{group_id}_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"show_group_tasks_{group_id}_{page + 1}"))

    if navigation_buttons:
        inline_keyboard.append(navigation_buttons)

    # Add a "Back to main menu" button
    inline_keyboard.append([InlineKeyboardButton(text="Назад к списку отделов", callback_data="show_task_list")])

    # Create the inline keyboard with task details and navigation buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    # Update the message to show task list and buttons
    await callback_query.message.edit_text(message, reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith("create_task"))
async def create_task(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(main_menu_message_id=callback_query.message.message_id)
    if "user" in callback_query.data:
        user_id = int(callback_query.data.split("_")[-1])
        await state.update_data({"assignee_id": user_id})
        print(f"Assignee ID: {user_id}")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    await callback_query.message.edit_text("Введите название задачи (Максимум 30 символ):", reply_markup=keyboard)
    await state.set_state(TaskCreationStates.waiting_for_task_title)
        
@router.message(StateFilter(TaskCreationStates.waiting_for_task_title))
async def process_task_title(message: types.Message, state: FSMContext):
    task_title = message.text
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    if len(task_title) > 30:
        await message.answer("Название задачи не должно превышать 30 символов. Пожалуйста, введите корректное название.", reply_markup=keyboard)
        return
    
    await state.update_data(waiting_for_task_title=task_title)
    await message.answer("Введите описание задачи:", reply_markup=keyboard)
    await state.set_state(TaskCreationStates.waiting_for_task_description)

@router.message(StateFilter(TaskCreationStates.waiting_for_task_description))
async def process_task_description(message: types.Message, state: FSMContext):
    task_description = message.text
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    await state.update_data(waiting_for_task_description=task_description)
    await message.answer("Введите начальную дату выполнения задачи в формате (дд.мм.гггг):", reply_markup=keyboard)
    await state.set_state(TaskCreationStates.waiting_for_task_start_date)

@router.message(StateFilter(TaskCreationStates.waiting_for_task_start_date))
async def process_task_start_date(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    task_start_date = message.text
    try:
        start_date_obj = datetime.strptime(task_start_date, '%d.%m.%Y')
        if start_date_obj.day < datetime.now().day - 1 or start_date_obj.month < datetime.now().month or start_date_obj.year < datetime.now().year:
            raise ValueError("Дата начала не может быть в прошлом.")
        elif start_date_obj.year > datetime.now().year + 1:
            raise ValueError(f"Год должен быть {datetime.now().year} или {datetime.now().year + 1}")
    except ValueError as e:
        print(f"Некорректный формат даты: {e}")
        await message.answer(f"{e}\nПожалуйста, введите дату начала в формате дд.мм.гггг.", reply_markup=keyboard)
        return
    
    await state.update_data(waiting_for_task_start_date=task_start_date)
    await message.answer("Введите конечную дату выполнения задачи в формате (дд.мм.гггг):", reply_markup=keyboard)
    await state.set_state(TaskCreationStates.waiting_for_task_due_date)

@router.message(StateFilter(TaskCreationStates.waiting_for_task_due_date))
async def process_task_due_date(message: types.Message, state: FSMContext):
    task_due_date = message.text
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    try:
        due_date_obj = datetime.strptime(task_due_date, '%d.%m.%Y')
        data = await state.get_data()
        task_start_date = data.get("waiting_for_task_start_date")
        if due_date_obj < datetime.now():
            raise ValueError("Дата завершения не может быть в прошлом.")
        elif due_date_obj.year > datetime.now().year + 1:
            raise ValueError(f"Год должен быть {datetime.now().year} или {datetime.now().year + 1}")
        elif due_date_obj < datetime.strptime(task_start_date, '%d.%m.%Y'):
            raise ValueError("Дата завершения не может быть раньше даты начала.")
    except ValueError as e:
        print(f"Некорректный формат даты: {e}")
        await message.answer(f"{e}\n Пожалуйста, введите дату завершения в формате дд.мм.гггг.", reply_markup=keyboard)
        return
    
    await state.update_data(waiting_for_task_due_date=task_due_date)
    await message.answer("Выберите приоритет задачи:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Низкий", callback_data="task_priority_low"),InlineKeyboardButton(text="Средний", callback_data="task_priority_medium"), InlineKeyboardButton(text="Высокий", callback_data="task_priority_high")],
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")]
        ]
    ))
    await state.set_state(TaskCreationStates.waiting_for_task_priority)

@router.callback_query(lambda call: call.data.startswith("task_priority_"))
async def process_task_priority(callback_query: types.CallbackQuery, state: FSMContext):
    task_priority = callback_query.data.split("_")[-1]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )

    priority = ''
    if task_priority == "low":
        priority = "Low"
    elif task_priority == "medium":
        priority = "Medium"
    elif task_priority == "high":
        priority = "High"
    
    await state.update_data({"waiting_for_task_priority": priority})
    data = await state.get_data()
    assignee_id = data.get("assignee_id")
    print(assignee_id)

    data = await state.get_data()
    task_title = data.get("waiting_for_task_title")
    task_description = data.get("waiting_for_task_description")
    task_start_date = data.get("waiting_for_task_start_date")
    task_due_date = data.get("waiting_for_task_due_date")
    task_priority = data.get("waiting_for_task_priority")

    if assignee_id is not None:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userToken, fullname FROM user WHERE id=?", (assignee_id,))
            user = cursor.fetchone()
            userToken, fullname = user
        await state.update_data({"waiting_for_task_assignee": assignee_id})
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить создание задачи", callback_data="confirm_task_creation")],
                [InlineKeyboardButton(text="Отменить создание задачи", callback_data="show_task_list")],
            ]
        )
        await callback_query.message.edit_text(f"Подтвердите создание задачи:\n\nИнформация о задаче:\nНазвание: {task_title}\nОписание: {task_description}\nНачальная дата: {task_start_date}\nКонечная дата: {task_due_date}\nПриоритет: {task_priority}\n\nСотрудник: {userToken} {fullname}\n\n", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("Введите ID(AA000) сотрудника, которому назначается задача:", reply_markup=keyboard)
        await state.set_state(TaskCreationStates.waiting_for_task_assignee)

@router.message(StateFilter(TaskCreationStates.waiting_for_task_assignee))
async def process_assignee_id(message: types.Message, state: FSMContext):
    userToken = message.text
    data = await state.get_data()
    task_title = data.get("waiting_for_task_title")
    task_description = data.get("waiting_for_task_description")
    task_start_date = data.get("waiting_for_task_start_date")
    task_due_date = data.get("waiting_for_task_due_date")
    task_priority = data.get("waiting_for_task_priority")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="show_task_list")],
        ]
    )
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, group_id FROM user WHERE userID=?", (message.from_user.id,))
        role, group_id = cursor.fetchone()
        if role == "Boss":
            cursor.execute("SELECT id as user_id, userID, fullname FROM user WHERE userToken = ?", (userToken,))
            user = cursor.fetchone()
        else:
            cursor.execute("SELECT id as user_id, userID, fullname FROM user WHERE userToken = ? AND group_id = ?", (userToken, group_id))
            user = cursor.fetchone()
    if not user:
        await message.answer("Сотрудник с таким ID не найден. Пожалуйста, введите корректный ID.", reply_markup=keyboard)
        return
    elif user[0] == message.from_user.id:
        await message.answer("Вы не можете назначить задачу самому себе. Пожалуйста, введите ID другого сотрудника.", reply_markup=keyboard)
        return

    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить создание задачи", callback_data="confirm_task_creation")],
            [InlineKeyboardButton(text="Отменить создание задачи", callback_data="show_task_list")],
        ]
    )
    user_id, userID, fullname = user
    await state.update_data(assignee_id=user_id)
    await message.answer(f"Подтвердите создание задачи:\n\nИнформация о задаче:\nНазвание: {task_title}\nОписание: {task_description}\nНачальная дата: {task_start_date}\nКонечная дата: {task_due_date}\nПриоритет: {task_priority}\n\nСотрудник: {userToken} {fullname}\n\n", reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "confirm_task_creation")
async def confirm_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    task_title = data.get("waiting_for_task_title")
    task_description = data.get("waiting_for_task_description")
    task_start_date = data.get("waiting_for_task_start_date")
    task_due_date = data.get("waiting_for_task_due_date")
    task_priority = data.get("waiting_for_task_priority")
    task_assignee_id = data.get("assignee_id")

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE userID=?", (callback_query.from_user.id,))
        task_owner_id = cursor.fetchone()[0]
        cursor.execute("SELECT userID FROM user WHERE id=?", (task_assignee_id,))
        worker_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO task (task_title, task_description, start_date, due_date, priority, task_assignee_id, task_owner_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (task_title, task_description, task_start_date, task_due_date, task_priority, task_assignee_id, task_owner_id, datetime.now().strftime('%H:%M:%S %d.%m.%Y')))
        conn.commit()

    # Notify the assignee about the new task
    
    await bot.send_message(worker_id, f"Вам назначена новая задача:\n\nНазвание: {task_title}\nОписание: {task_description}\nНачальная дата: {task_start_date}\nКонечная дата: {task_due_date}\nПриоритет: {task_priority}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Посмотреть задачу", callback_data=f"task_{cursor.lastrowid}")]]))
    await callback_query.message.answer("Задача успешно создана и назначена сотруднику.", reply_markup=ReplyKeyboardRemove())
    await show_task_list(callback_query, state)

    await state.clear()  # Ensure the coroutine is awaited
        
@router.callback_query(lambda call: call.data.startswith("task_"))
async def show_task_details(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT
                        t.task_title,
                        t.task_description,
                        t.start_date,
                        t.due_date,
                        t.priority,
                        t.status,
                        t.created_at,
                        t.started_at,
                        t.paused_at,
                        t.continued_at,
                        t.finished_at,
                        u.userID as assignee_userID,
                        u.userToken as assignee_userToken,
                        u.fullname as assignee_fullname,
                        u2.userID as owner_userID,
                        u2.userToken as owner_userToken,
                        u2.fullname as owner_fullname,
                        u2.role as owner_role
                    FROM
                        task t
                        JOIN user u ON t.task_assignee_id = u.id
                        JOIN user u2 ON t.task_owner_id = u2.id
                    WHERE
                        t.id = ?
        """, (task_id,))
        details = cursor.fetchone()
        if details:
            task_title, task_description, start_date, due_date, priority, status, created_at, started_at, paused_at, continued_at, finished_at, assignee_userID, assignee_userToken, assignee_fullname, owner_userID, owner_userToken, owner_fullname, owner_role = details
            message = (
                f"Информация о задаче:\n"
                f"Название: {task_title}\n"
                f"Описание: {task_description}\n"
                f"Начальная дата: {start_date}\n"
                f"Конечная дата: {due_date}\n"
                f"Приоритет: {priority}\n"
                f"Статус: {status}\n"
                f"Создана: {created_at}\n"
                f"Назначена: {assignee_userToken} {assignee_fullname}\n"
                f"Создатель: {owner_userToken} {owner_fullname} ({"Администратор отдела" if owner_role == "Manager" else "Директор компании"})\n\n"
            )
            if started_at is not None:
                message += f"Начата: {started_at}\n"
            if paused_at is not None:
                message += f"Приостановлена: {paused_at}\n"
            if continued_at is not None:
                message += f"Продолжена: {continued_at}\n"
            if finished_at is not None:
                message += f"Завершена: {finished_at}\n"

            inline_keyboard = []
            if assignee_userID == callback_query.from_user.id:
                if status == 'Not started':
                    inline_keyboard.append([InlineKeyboardButton(text="Начать выполнение", callback_data=f"start_task_{task_id}")])
                elif status == 'In progress':
                    inline_keyboard.append([InlineKeyboardButton(text="Пауза", callback_data=f"pause_task_{task_id}"), InlineKeyboardButton(text="Завершить задачу", callback_data=f"finish_task_{task_id}")])
                elif status == 'Paused':
                    inline_keyboard.append([InlineKeyboardButton(text="Продолжить", callback_data=f"resume_task_{task_id}")])
                else:
                    message += "\nЗадача завершена."
            elif owner_userID == callback_query.from_user.id:
                inline_keyboard.append([InlineKeyboardButton(text="Удалить задачу", callback_data=f"delete_task_{task_id}")])
                inline_keyboard.append([InlineKeyboardButton(text="Изменить данные", callback_data=f"change_task_details_{task_id}")])
            inline_keyboard.append([InlineKeyboardButton(text="Назад к списку задач", callback_data="show_task_list")])

            keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

            await callback_query.message.edit_text(message, reply_markup=keyboard)
            await state.update_data({"main_menu_message_id": callback_query.message.message_id})

@router.callback_query(lambda call: call.data.startswith("start_task_"))
async def start_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])

    # Update task status in the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET status = 'In progress', started_at = ? WHERE id = ?", (datetime.now().strftime('%H:%M:%S %d.%m.%Y'), task_id))
        conn.commit()

    # Update the message
    await show_task_details(callback_query, state)

    # Send alert
    await callback_query.answer("Задача начата.", show_alert=True)

@router.callback_query(lambda call: call.data.startswith("pause_task_"))
async def pause_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])

    # Update task status in the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET status = 'Paused', paused_at = ? WHERE id = ?", (datetime.now().strftime('%H:%M:%S %d.%m.%Y'), task_id))
        conn.commit()

    # Update the message
    await show_task_details(callback_query, state)

    # Send alert
    await callback_query.answer("Задача приостановлена.", show_alert=True)

@router.callback_query(lambda call: call.data.startswith("resume_task_"))
async def resume_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])

    # Update task status in the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET status = 'In progress', continued_at = ? WHERE id = ?", (datetime.now().strftime('%H:%M:%S %d.%m.%Y'), task_id))
        conn.commit()

    # Update the message
    await show_task_details(callback_query, state)

    # Send alert
    await callback_query.answer("Задача продолжена.", show_alert=True)


@router.callback_query(lambda call: call.data.startswith("finish_task_"))
async def finish_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])

    # Update task status in the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET status = 'Finished', finished_at = ? WHERE id = ?", (datetime.now().strftime('%H:%M:%S %d.%m.%Y'), task_id))
        conn.commit()

    # Update the message
    await show_task_details(callback_query, state)

    # Send alert
    await callback_query.answer("Задача завершена.", show_alert=True)

async def notify_user_on_reload():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT userID FROM user")
        user = cursor.fetchall()
        for user in user:
            try:
                await bot.send_message(user[0], "Бот был перезагружен. Пожалуйста, напишите команду /start, чтобы продолжить.")
            except Exception as e:
                print(f"Error sending message to user {user[0]}")

dp.include_router(router)

async def main():
    await notify_user_on_reload()

    await dp.start_polling(bot)

if __name__ == '__main__':
    init_db()
    asyncio.run(main())
