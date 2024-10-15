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
from datetime import datetime

API_TOKEN = '7314896845:AAE4AXQdXTaeaN-BfegtS2EbzHKi7U68OOw'

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

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userID INTEGER NOT NULL UNIQUE,
                        userToken INTEGER NOT NULL UNIQUE,
                        fullname TEXT,
                        phone_number TEXT,
                        position TEXT,
                        birthdate TEXT,
                        role TEXT NOT NULL DEFAULT 'Boss',
                        company_id INTEGER DEFAULT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

async def ask_for_next_missing_field(message: types.Message, state: FSMContext):
    userID = message.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id FROM users WHERE userID = ?", (userID,))
        user = cursor.fetchone()

    fullname, phone_number, position, birthdate, company_id = user

    if not fullname:
        await message.answer("Напишите полное имя:")
        await state.set_state(RegistrationStates.waiting_for_fullname)
    elif not phone_number:
        await ask_for_phone_number(message, state)
    elif not position:
        await message.answer("Введите вашу должность:")
        await state.set_state(RegistrationStates.waiting_for_position)
    elif not birthdate:
        await message.answer("Введите вашу дату рождения в формате (дд.мм.гггг):")
        await state.set_state(RegistrationStates.waiting_for_birthdate)
    elif not company_id:
        await message.answer("Пожалуйста, введите название вашей компании для создания:")
        await state.set_state(RegistrationStates.waiting_for_company)
    else:
        return True
    return False

async def generate_user_token():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(userToken) FROM users")
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

@router.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    userID = message.from_user.id
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id FROM users WHERE userID = ?", (userID, ))
        user = cursor.fetchone()
        userToken = await generate_user_token()
        
        if user:
            role, company_id = user
            complete = await ask_for_next_missing_field(message, state)
            if complete:
                if role == 'Boss' and not company_id:
                    await ask_for_company(message, state)
                else:
                    await message.answer("Вы уже зарегистрированы и присоединены к компании. Добро пожаловать!")
                    await main_menu(message, state, role=role)
        else:
            cursor.execute("INSERT OR IGNORE INTO users (userID, userToken) VALUES (?, ?)", (userID, userToken,))
            conn.commit()
            await message.reply("Добро пожаловать! Пожалуйста, давайте приступим к процессу регистрации.")
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
    phone_number = message.contact.phone_number if message.contact else message.text
    
    if not re.match(r'^\+998\d{9}$', phone_number):
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX.")
        return
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET phone_number=? WHERE userID=?", (phone_number, message.from_user.id))
        conn.commit()
    
    await message.answer("Телефон успешно сохранен.", reply_markup=ReplyKeyboardRemove())
    await ask_for_next_missing_field(message, state)

@router.message(StateFilter(RegistrationStates.waiting_for_fullname))
async def process_fullname(message: types.Message, state: FSMContext):
    fullname = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET fullname=? WHERE userID=?", (fullname, message.from_user.id))
        conn.commit()
    
    await ask_for_next_missing_field(message, state)

@router.message(StateFilter(RegistrationStates.waiting_for_position))
async def process_position(message: types.Message, state: FSMContext):
    position = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET position=? WHERE userID=?", (position, message.from_user.id))
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
        await message.answer(f"Некорректный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг.")
        return
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET birthdate=? WHERE userID=?", (birthdate, message.from_user.id))
        conn.commit()

    await ask_for_next_missing_field(message, state)

async def ask_for_company(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите название вашей компании для создания:")
    await state.set_state(CompanySettingsStates.waiting_for_company_name)

@router.message(StateFilter(CompanySettingsStates.waiting_for_company_name))
async def process_company(message: types.Message, state: FSMContext):
    company_name = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE company_name=?", (company_name,))
        company = cursor.fetchone()

        cursor.execute("SELECT role FROM users WHERE userID=?", (message.from_user.id, ))
        role = cursor.fetchone()[0]
        
        if company:
            await message.answer(f"Компания '{company_name}' уже существует. Пожалуйста, введите другое название. Если вы не являетесь администратором компании, обратитесь к администратору.")
            return
        else:
            cursor.execute("INSERT INTO companies (company_name) VALUES (?)", (company_name,))
            company_id = cursor.lastrowid
            
            cursor.execute("UPDATE users SET company_id=? WHERE userID=?", (company_id, message.from_user.id))
            conn.commit()

            await main_menu(message, state, role)

    await state.clear()


async def main_menu(message: types.Message, state: FSMContext, role):
    if role == 'Boss':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings"), InlineKeyboardButton(text="Настройки компании", callback_data="company_settings")],
            ]
        )

        sent_message = await message.answer("Главное меню", reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)

    elif role == "Manager":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees"), InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings")],
            ]
        )
        sent_message = await message.answer("Главное меню", reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)

    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Список задач", callback_data="task_list")],
                [InlineKeyboardButton(text="Профиль", callback_data="user_settings")],
            ]
        )
        sent_message = await message.answer("Главное меню", reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)

@router.callback_query(lambda call: call.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE userID=?", (callback_query.from_user.id,))
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
        cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id FROM users WHERE userID=?", (callback_query.from_user.id,))
        user = cursor.fetchone()
        fullname, phone_number, position, birthdate, company_id = user
        cursor.execute("SELECT company_name FROM companies WHERE id=?", (company_id,))
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
        cursor.execute("SELECT fullname, phone_number, position, birthdate, company_id FROM users WHERE userID=?", (message.from_user.id,))
        user = cursor.fetchone()
        fullname, phone_number, position, birthdate, company_id = user
        cursor.execute("SELECT company_name FROM companies WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        user_data_message = f"Ваши данные:\nФИО: {fullname}\nТелефон: {phone_number}\nДолжность: {position}\nДата рождения: {birthdate}\nВаша компания: {company_name}"
    
    await message.answer(user_data_message, reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "show_change_data_menu")
async def show_change_data_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить ФИО", callback_data="change_fullname")],
            [InlineKeyboardButton(text="Изменить телефон", callback_data="change_phone")],
            [InlineKeyboardButton(text="Изменить должность", callback_data="change_position")],
            [InlineKeyboardButton(text="Изменить дату рождения", callback_data="change_birthdate")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_user_settings")],
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
        cursor.execute("UPDATE users SET fullname=? WHERE userID=?", (fullname, message.from_user.id))
        conn.commit()
    
    await message.answer("ФИО успешно изменено.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)

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
    
    if not re.match(r'^\+998\d{9}$', phone_number):
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX.")
        return
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET phone_number=? WHERE userID=?", (phone_number, message.from_user.id))
        conn.commit()
    
    await message.answer("Телефон успешно изменен.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)

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
        cursor.execute("UPDATE users SET position=? WHERE userID=?", (position, message.from_user.id))
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
        cursor.execute("UPDATE users SET birthdate=? WHERE userID=?", (birthdate, message.from_user.id))
        conn.commit()

    await message.answer("Дата рождения успешно изменена.", reply_markup=ReplyKeyboardRemove())
    await show_user_settings_for_message(message, state)

@router.callback_query(lambda call: call.data == "company_settings")
async def show_company_settings(callback_query: types.CallbackQuery):
    userID = callback_query.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM users WHERE userID=?", (userID,))
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT company_name FROM companies WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        workerCount = cursor.execute("SELECT COUNT(*) FROM users WHERE company_id=?", (company_id,)).fetchone()[0]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees")],
            [InlineKeyboardButton(text="Изменить название компании", callback_data="change_company_name")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
        ]
    )
    await callback_query.message.edit_text(f"Здравствуйте, администратор компании!\nВаша компания {company_name}.\nЧисло сотрудников: {workerCount}\n\nХотите что-нибудь изменить?", reply_markup=keyboard)

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
    company_name = message.text
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM users WHERE userID=?", (message.from_user.id,))
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM companies WHERE company_name=?", (company_name,))
        company = cursor.fetchone()

        if company:
            await message.answer(f"Компания '{company_name}' уже существует. Пожалуйста, введите другое название.")
            return
        else:
            cursor.execute("UPDATE companies SET company_name=? WHERE id=?", (company_name, company_id))
            conn.commit()

            await show_company_settings_msg(message)

    await state.clear()

async def show_company_settings_msg(message: types.Message):
    userID = message.from_user.id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM users WHERE userID=?", (userID,))
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT company_name FROM companies WHERE id=?", (company_id,))
        company_name = cursor.fetchone()[0]
        workerCount = cursor.execute("SELECT COUNT(*) FROM users WHERE company_id=?", (company_id,)).fetchone()[0]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список сотрудников", callback_data="list_of_employees")],
            [InlineKeyboardButton(text="Изменить название компании", callback_data="change_company_name")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")],
        ]
    )
    await message.answer(f"Здравствуйте, администратор компании!\nВаша компания {company_name}.\nЧисло сотрудников: {workerCount}\n\nХотите что-нибудь изменить?", reply_markup=keyboard)

@router.callback_query(lambda call: call.data == "referrer_links")
async def show_referral_links(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали: Реферальные ссылки.")

@router.callback_query(lambda call: call.data == "list_of_employees")
async def show_list_of_employees(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали: Список сотрудников.")

@router.callback_query(lambda call: call.data == "task_list")
async def show_task_list(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали: Список задач.")

async def notify_users_on_reload():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT userID FROM users")
        users = cursor.fetchall()
        for user in users:
            try:
                await bot.send_message(user[0], "Бот был перезагружен. Пожалуйста, напишите команду /start, чтобы продолжить.")
            except Exception as e:
                print(f"Error sending message to user {user[0]}: {e}")

dp.include_router(router)

async def main():
    await notify_users_on_reload()

    await dp.start_polling(bot)

if __name__ == '__main__':
    init_db()
    asyncio.run(main())
