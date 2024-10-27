import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram import Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import asyncio
import re

from db_utils import *

from config import API_TOKEN, BOT_USERNAME

from btns import main_menu_btns
from company.show_company import show_company
from company.list_company_workers import list_workers
from company.show_departments import show_departments
from company.list_department_workers import list_department_workers
from company.referal_links import show_referal_links

# Initialize bot and storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

router.callback_query.register(show_company, F.data == "company")
router.callback_query.register(list_workers, F.data.startswith("list_workers"))
router.callback_query.register(show_departments, F.data.startswith("departments"))
router.callback_query.register(list_department_workers, F.data.startswith("show_department_"))
router.callback_query.register(show_referal_links, F.data == "referral_links")

# Define bot states
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

@router.message(F.text.startswith('/start'))
async def start_command(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    user_id = message.from_user.id

    # Check if user exists; if not, add them with role_id=1 (Boss)
    user = await get_user(user_id)
    args = message.text.split(" ", 1)
    company_id = None
    department_id = None

    await state.update_data(main_menu_message_id=0)

    # If there are any arguments after /start, parse them
    if len(args) > 1 and args[1]:
        try:
            # Assuming that the format is "1_group=1", split it
            params = args[1].split('_')
            company_id = params[0]
            if len(params) > 1:
                department_id = params[1].split('=')[1]  # Extract department_id from "group=1"

            print(f"Parsed company_id: {company_id}, department_id: {department_id}, user_id: {user_id}")  # Debugging info
        except Exception as e:
            print(f"Error parsing arguments: {e}")
            await message.reply("Ошибка в параметрах ссылки. Пожалуйста, проверьте правильность ссылки.")
            return

    text = """Привет! Я помогу тебе управлять проектами. Для начала, выберите язык.
    
---------------------------------------------------------------------

Salom! Men sizga loyihalarni boshqarishda yordam beraman. Boshlash uchun tilni tanlang."""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")
        ]
    ])
    
    # Correct usage of db_pool.acquire with parentheses
    async with db_pool.acquire() as connection:
        if user is None:
            await connection.execute("INSERT INTO users (user_id, role_id) VALUES ($1, 1) ON CONFLICT (user_id) DO NOTHING", user_id)
            send_message = await message.answer(text, reply_markup=keyboard)
            await state.update_data(main_menu_message_id=send_message.message_id)
        else:
            await navigate_to_main_menu(user_id, message.chat.id, state)

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id != callback.message.message_id:
        await callback.answer("This button is no longer active.")
        return
    # Respond to the callback query to avoid the alert
    await callback.answer()

    # Debugging to check if the callback handler is triggered
    print(f"Language set to: {lang} for user: {user_id}")

    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET lang = $1 WHERE user_id = $2", lang, user_id)

    # Move to registration state
    if lang == 'ru':
        await callback.message.answer("Для регистрации введите ваше имя.")
    elif lang == 'uz':
        await callback.message.answer("Ro'yxatdan o'tish uchun ismingizni kiriting.")

    await state.set_state(RegistrationStates.fullname)


@router.message(StateFilter(RegistrationStates.fullname))
async def process_fullname(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    fullname = message.text

    # Correct usage of db_pool.acquire
    async with db_pool.acquire() as connection:
        await connection.execute("UPDATE users SET fullname = $1 WHERE user_id = $2", fullname, message.from_user.id)
    
    await state.set_state(RegistrationStates.phone_number)
    lang = await get_user_lang(message.from_user.id)
    if lang == 'ru':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Введите правильный номер телефона в формате +998XXXXXXXXX или нажмите кнопку ниже", reply_markup=keyboard)
    elif lang == 'uz':
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("To'g'ri telefon raqamni +998XXXXXXXXX formatda kiriting yoki pastdagi tugmani bosing", reply_markup=keyboard)

@router.message(StateFilter(RegistrationStates.phone_number))
async def process_phone_number(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    phone_number = message.contact.phone_number if message.contact else message.text
    lang = await get_user_lang(message.from_user.id)

    normalized_phone_number = phone_number.lstrip('+')

    # Check if the phone number matches the expected format
    if re.match(r'^998\d{9}$', normalized_phone_number):
        async with db_pool.acquire() as connection:
            await connection.execute("UPDATE users SET phone_number = $1 WHERE user_id = $2", phone_number, message.from_user.id)

            await state.set_state(RegistrationStates.birthdate)
            if lang == 'ru':
                await message.answer("Телефон успешно сохранен. Теперь введите вашу дату рождения в формате ДД.ММ.ГГГГ", reply_markup=ReplyKeyboardRemove())
            elif lang == 'uz':
                await message.answer("Telefon muvaffaqiyatli saqlandi. Endi tug'ilgan kuningizni KK.OO.YYYY formatda kiriting", reply_markup=ReplyKeyboardRemove())
    else:
        if lang == 'ru':
            await message.answer("Номер телефона введен неверно. Пожалуйста, введите номер в формате +998XXXXXXXXX")
        elif lang == 'uz':
            await message.answer("Telefon raqami noto'g'ri kiritildi. Iltimos, telefon raqamini +998XXXXXXXXX formatda kiriting")

@router.message(StateFilter(RegistrationStates.birthdate))
async def process_birthdate(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    birthdate = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(message.from_user.id)

    try:
        date_obj = datetime.datetime.strptime(birthdate, "%d.%m.%Y")
        current_year = datetime.datetime.now().year

        if date_obj.year < 1920 or date_obj.year > 2020:
            if lang == 'ru':
                raise ValueError("Год должен быть между 1920 и 2020")
            elif lang == 'uz':
                raise ValueError("Yil 1920 va 2020 oralig'ida bo'lishi kerak")
            return

        if date_obj > datetime.datetime.now():
            if lang == 'ru':
                raise ValueError("Дата рождения не может быть в будущем")
            elif lang == 'uz':
                raise ValueError("Tug'ilgan kun kelgusida bo'lishi mumkin emas")
            return

        # If the birthdate is valid, update it in the database
        async with db_pool.acquire() as connection:
            await connection.execute("""
                UPDATE users SET birthdate = $1 WHERE user_id = $2
            """, date_obj.date(), message.from_user.id)
            user_role = await connection.fetchval("SELECT role_id FROM users WHERE user_id = $1", user_id)

        if lang == 'ru':
            await message.answer("Дата рождения успешно сохранена.")
        elif lang == 'uz':
            await message.answer("Tug'ilgan kun muvaffaqiyatli saqlandi.")

        # Proceed to the next state
        if user_role == 1:
            await state.set_state(CompanyCreation.company_name)
            if lang == 'ru':
                await message.answer("Теперь введите название вашей компании")
            elif lang == 'uz':
                await message.answer("Endi kompaniya nomini kiriting")
        else:
            await state.clear()
            if lang == 'ru':
                await message.answer("Вы успешно завершили регистрацию")
            elif lang == 'uz':
                await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz")
    except ValueError:
        if lang == 'ru':
            await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")
        elif lang == 'uz':
            await message.answer("Noto'g'ri sana formati. Iltimos, sanani KK.OO.YYYY formatda kiriting")

@router.message(StateFilter(CompanyCreation.company_name))
async def process_company_name(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    company_name = message.text
    lang = await get_user_lang(message.from_user.id)

    async with db_pool.acquire() as connection:
        await connection.execute("INSERT INTO company (company_name) VALUES ($1)", company_name)
        company_id = await connection.fetchval("SELECT id FROM company WHERE company_name = $1", company_name)
        await connection.execute("UPDATE users SET company_id = $1 WHERE user_id = $2", company_id, message.from_user.id)

    await state.set_state(DepartmentCreation.department_name)
    if lang == 'ru':
        await message.answer("Вы успешно завершили регистрацию. Теперь, давайте добавим название отдела или рабочий группы.")
    elif lang == 'uz':
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Endi, bo'lim yoki ish guruhi nomini qo'shaylik.")


@router.message(StateFilter(DepartmentCreation.department_name))
async def process_department_name(message: types.Message, state: FSMContext):
    db_pool = get_db_pool()
    department_name = message.text
    lang = await get_user_lang(message.from_user.id)

    async with db_pool.acquire() as connection:
        company_id = await connection.fetchval("SELECT company_id FROM users WHERE user_id = $1", message.from_user.id)
        await connection.execute("INSERT INTO department (department_name, company_id) VALUES ($1, $2)", department_name, company_id)
        department_id = await connection.fetchval("SELECT id FROM department WHERE department_name = $1", department_name)
        department_name = await connection.fetchval("SELECT department_name FROM department WHERE id = $1", department_id)

    # Prepare referral link for the newly created department
    referral_link = f"https://t.me/{BOT_USERNAME}?start={company_id}_group={department_id}"
    share_link = (
        f"https://t.me/share/url?url={referral_link}&text=Join our team in the {department_name} department."
    )

    if lang == 'ru':
        department_msg = (
            f"Отдел '{department_name}' успешно создан! Вы можете продолжить добавлять отделы или нажать 'Завершить' для выхода."
        )
        continue_text = "Продолжить"
        finish_text = "Завершить"
    else:
        department_msg = (
            f"'{department_name}' bo‘limi muvaffaqiyatli yaratildi! Bo‘lim qo‘shishni davom ettiring yoki chiqish uchun 'Tugatish' tugmasini bosing."
        )
        continue_text = "Davom etish"
        finish_text = "Tugatish"

    # Options for the user to continue adding departments or finish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=continue_text, callback_data="continue_department_creation")],
        [InlineKeyboardButton(text=finish_text, callback_data="finish_department_creation")]
    ])

    send_message = await message.answer(department_msg, reply_markup=keyboard)
    await state.update_data(main_menu_message_id= send_message.message_id + 1)

@router.callback_query(F.data == "continue_department_creation")
async def continue_department_creation(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)

    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id != callback.message.message_id + 1:
        await callback.answer(f"This button is no longer active.", show_alert=True)
        return

    if lang == 'ru':
        prompt_text = "Введите название следующего отдела."
    else:
        prompt_text = "Keyingi bo‘lim nomini kiriting."

    await callback.message.edit_text(prompt_text)
    await state.set_state(DepartmentCreation.department_name)

@router.callback_query(F.data == "finish_department_creation")
async def finish_department_creation(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)

    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    if main_menu_message_id != callback.message.message_id + 1:
        await callback.answer("This button is no longer active.")
        return
    
    await state.clear()  # Exit the department creation loop

    async with get_db_pool().acquire() as connection:
        company_id = await connection.fetchval("SELECT company_id FROM users WHERE user_id = $1", callback.from_user.id)
        departments = await connection.fetch("SELECT * FROM department WHERE company_id = $1", company_id)
    
    keyboard = []

    if lang == 'ru':
        for department in departments:
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company_id}_group={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Ребята, нажмите, пожалуйста, на ссылку, чтобы получить задачу от начальства."
            keyboard.append([InlineKeyboardButton(text=f"Отдел: {department['department_name']}", url=share_link)])
        await callback.message.edit_text("""
Теперь отправьте реферальную ссылку руководителю этого отдела. Он добавит всех участников этой группы или Вы сами можете добавить участников нажимая следующую кнопку с названием отдела. В кнопках указаны названия отделов.

P.s: Первый кто зайдет по этой ссылке будет руководителем. Но не переживай, в любой момент можете изменить должность сотрудников в настройках.""",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        for department in departments:
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company_id}_group={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Yigitlar, boshliqdan vazifa olish uchun quyidagi havolaga kiring."
            keyboard.append([InlineKeyboardButton(text=f"Bo'lim: {department['department_name']}", url=share_link)])
        await callback.message.edit_text("""
Endi bu bo‘lim rahbariga tavsiya havolani yuboring. U bu guruhdagi barcha a'zolarni qo‘shadi yoki siz o‘ziz qo‘shishingiz mumkin. Bo‘lim nomi tugmasini bosing.
                                         
P.s: Bu havolaga birinchi kiringan odam bo‘lib qoladi. Lekin xavotir bo‘lmang, har qanday vaqtda xodimlar vazifalarini sozlamalarda o‘zgartirishingiz mumkin.""")

    await navigate_to_main_menu(callback.from_user.id, callback.message.chat.id, state)

async def navigate_to_main_menu(user_id: int, chat_id: int, state: FSMContext):
    db_pool = get_db_pool()
    """Navigates the user back to the main menu, displaying options based on role and language."""
    # Retrieve main menu message ID from state
    data = await state.get_data()
    main_menu_message_id = data.get("main_menu_message_id")

    # Fetch user details: role and language
    async with db_pool.acquire() as connection:
        user = await connection.fetchrow("SELECT role_id, lang FROM users WHERE user_id = $1", user_id)
    
    if user is None:
        await bot.send_message(chat_id, "User not found. Please register again with /start.")
        return

    lang = user['lang']

    # Set up menu text and dynamically create keyboard based on role and language
    main_menu_text = "Главное меню" if lang == 'ru' else "Asosiy menyum"
    keyboard = main_menu_btns[lang]

    # Attempt to edit the existing main menu message or send a new one if editing fails
    if main_menu_message_id:
        try:
            await bot.edit_message_text(
                main_menu_text, chat_id=chat_id,
                message_id=main_menu_message_id, reply_markup=keyboard
            )
        except Exception:
            sent_message = await bot.send_message(chat_id, main_menu_text, reply_markup=keyboard)
            await state.update_data(main_menu_message_id=sent_message.message_id)
    else:
        sent_message = await bot.send_message(chat_id, main_menu_text, reply_markup=keyboard)
        await state.update_data(main_menu_message_id=sent_message.message_id)

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    db_pool = get_db_pool()
    data = await state.get_data()
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    """Handles navigating back to the main menu, using role-based logic."""
    await callback.message.delete()  # Optionally delete the previous message
    await navigate_to_main_menu(callback.from_user.id, callback.message.chat.id, state)  # Go to main menu
    
@router.message(F.text == "/deletedb")
async def delete_db(message: types.Message):
    db_pool = get_db_pool()
    """Deletes all tables from the database."""
    async with db_pool.acquire() as connection:
        await connection.execute("""
            DELETE FROM users;
            DELETE FROM task;
            DELETE FROM user_m2m_project;
            DELETE FROM project;
            DELETE FROM department;
            DELETE FROM company;
        """)
    await message.answer("All tables have been deleted.")

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
