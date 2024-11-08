from datetime import datetime
from aiogram.fsm.context import FSMContext
from btns import back_to_main, back_page
from config import API_TOKEN
from database.db_utils import get_db_pool, get_user, get_user_lang
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, Bot

from menu.main_menu import navigate_to_main_menu
from states import TaskChanges
from utils.date_function import parse_and_validate_date
from utils.priority_parser import parse_priority_id

bot = Bot(token=API_TOKEN)

async def edit_task_info(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    task_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    db = get_db_pool()
    user = await get_user(user_id)
    lang = user['lang']

    text = {
        "en": "Select what you want to change in the task",
        "ru": "Выберите, что вы хотите изменить в задаче",
        "uz": "Vazifada o'zgartirishni istaganini tanlang"
    }

    setting_text = {
        "en": {
            "title": "Title",
            "description": "Description",
            "date": "Task date",
            "priority": "Priority"
        },
        "ru": {
            "title": "Название",
            "description": "Описание",
            "date": "Дата задачи",
            "priority": "Приоритет"
        },
        "uz": {
            "title": "Sarlavha",
            "description": "Tavsif",
            "date": "Vazifa sanasi",
            "priority": "Urg'uli"
        }
    }

    keyboard = []

    for key, value in setting_text[lang].items():
        keyboard.append([InlineKeyboardButton(text=value, callback_data=f"edit_info_task_{key}_{task_id}")])
        print(key, value)

    keyboard_text = {
        "en": "🔙Back",
        "ru": "🔙Назад",
        "uz": "🔙Orqaga"
    }
    keyboard.append([InlineKeyboardButton(text=keyboard_text[lang], callback_data=f"task_info_{task_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(text[lang], reply_markup=markup)
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.update_data(task_id=task_id)

async def edit_task_key_info(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    data = await state.get_data()
    task_id = int(data.get("task_id"))
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    key = callback.data.split('_')[-2]

    keyboard = []

    if key == "title":
        text = {
            "en": "Enter new title",
            "ru": "Введите новое название",
            "uz": "Yangi sarlavhani kiriting"
        }
        await state.set_state(TaskChanges.task_title)
    elif key == "description":
        text = {
            "en": "Enter new description",
            "ru": "Введите новое описание",
            "uz": "Yangi tavsifni kiriting"
        }
        await state.set_state(TaskChanges.task_description)
    elif key == "date":
        text = {
            "en": "Enter new start date",
            "ru": "Введите новую дату начала",
            "uz": "Yangi boshlash sanasini kiriting"
        }
        keyboard_text = {
            "en": "📅Select today's date",
            "ru": "📅Выбрать сегодняшнюю дату",
            "uz": "📅Bugungi sanani tanlash"
        }
        keyboard.append([InlineKeyboardButton(text=keyboard_text[lang], callback_data=f"edit_today_date_{task_id}")])
        await state.set_state(TaskChanges.new_start_date)
    elif key == "priority":
        text = {
            "en": "Enter new priority",
            "ru": "Введите новый приоритет",
            "uz": "Yangi urg'uli kiriting"
        }
        keyboard_text = {
            "en": {
                "low": "Low",
                "medium": "Medium",
                "high": "High"
            },
            "ru": {
                "low": "Низкий",
                "medium": "Средний",
                "high": "Высокий"
            },
            "uz": {
                "low": "Past",
                "medium": "O'rta",
                "high": "Yuqori"
            }
        }
        keyboard.append([InlineKeyboardButton(keyboard_text[lang]["low"], callback_data=f"edit_priority_task_{task_id}_low"), 
                         InlineKeyboardButton(keyboard_text[lang]["medium"], callback_data=f"edit_priority_task_{task_id}_medium"), 
                         InlineKeyboardButton(keyboard_text[lang]["high"], callback_data=f"edit_priority_task_{task_id}_high")])
        await state.set_state(TaskChanges.priority)

    keyboard.append([InlineKeyboardButton(text=back_page[lang], callback_data=f"edit_task_{task_id}")])

    await callback.message.edit_text(text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)

async def edit_task_title(message: types.Message, state: FSMContext):
    task_id = int((await state.get_data())["task_id"])
    title = message.text
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    error_text = {
        "en": "Title must be less than 30 characters",
        "ru": "Название должно быть менее 30 символов",
        "uz": "Sarlavha 30 ta belgidan kam bo'lishi kerak"
    }

    if len(title) > 30:
        await message.answer(error_text[lang])
        return

    db = get_db_pool()
    async with db.acquire() as conn:
        task = await conn.fetchrow("SELECT * FROM task WHERE id = $1", task_id)
        worker_id = task["task_assignee_id"]
        worker = await conn.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        await conn.execute("UPDATE task SET task_title = $1 WHERE id = $2", title, task_id)

    text = {
        "en": f"The task \"{task['task_title']}\" title has been changed to {title}",
        "ru": f"Название задачи \"{task['task_title']}\" было изменено на {title}",
        "uz": f"Vazifa \"{task['task_title']}\" sarlavhasi {title} ga o'zgartirildi"
    }

    await message.answer(text[lang])
    await bot.send_message(worker["user_id"], text[lang])
    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)

async def edit_task_description(message: types.Message, state: FSMContext):
    task_id = int((await state.get_data())["task_id"])
    description = message.text
    user_id = message.from_user.id

    db = get_db_pool()
    async with db.acquire() as conn:
        task = await db.fetchrow("SELECT * FROM task WHERE id = $1", task_id)
        worker_id = task["task_assignee_id"]
        worker = await conn.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        await db.execute("UPDATE task SET task_description = $1 WHERE id = $2", description, task_id)

    lang = await get_user_lang(user_id)
    text = {
        "en": f"The task \"{task['task_title']}\" description has been changed to {description}",
        "ru": f"Описание задачи \"{task['task_title']}\" было изменено на {description}",
        "uz": f"Vazifa \"{task['task_title']}\" tavsifi {description} ga o'zgartirildi"
    }

    await message.answer(text[lang])
    await bot.send_message(worker["user_id"], text[lang])
    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)

async def edit_task_start_date(message: types.Message, state: FSMContext):
    task_id = int((await state.get_data())["task_id"])
    start_date_str = parse_and_validate_date(message.text)
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
    user_id = message.from_user.id

    db = get_db_pool()
    async with db.acquire() as conn:
        task = await db.fetchrow("SELECT * FROM task WHERE id = $1", task_id)
        worker_id = task["task_assignee_id"]
        worker = await conn.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        await db.execute("UPDATE task SET start_date = $1 WHERE id = $2", start_date, task_id)

    lang = await get_user_lang(user_id)
    text = {
        "en": f"The task \"{task['task_title']}\" start date has been changed to {start_date}",
        "ru": f"Дата начала задачи \"{task['task_title']}\" была изменена на {start_date}",
        "uz": f"Vazifa \"{task['task_title']}\" boshlash sanasi {start_date} ga o'zgartirildi"
    }

    await message.answer(text[lang])
    await bot.send_message(worker["user_id"], text[lang])
    await state.set_state(TaskChanges.new_due_date)

async def edit_today_date(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    # Verify that the callback message is still active
    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    # Set start date to today's date in 'dd.mm' format and validate it
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    start_date_str = parse_and_validate_date("today") 
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()

    # Update state with the validated start date
    db = get_db_pool()
    task_id = int((await state.get_data())["task_id"])
    await db.execute("UPDATE task SET start_date = $1 WHERE id = $2", start_date, task_id)
    await state.update_data(new_start_date=start_date_str)

    # Prepare the keyboard and send a confirmation message in the user's language
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_main[lang]]])

    send_texts = {
        'en': "Start date set to today. Now please enter the due date of the task in the format: **dd.mm** or **dd.mm.yy**",
        'ru': "Дата начала установлена на сегодня. Теперь введите дату завершения задачи в формате: **дд.мм** или **дд.мм.гг**",
        'uz': "Boshlash sanasi bugungi kunga sozlandi. Endi vazifaning tugash sanasini quyidagi formatda kiriting: **kk.oy** yoki **kk.oy.yy**"
    }
    send_text = send_texts.get(lang, send_texts['en'])

    # Edit the callback message and update the state
    await callback.message.edit_text(send_text, parse_mode="Markdown", reply_markup=keyboard)
    await state.update_data(main_menu_message_id=callback.message.message_id)
    await state.set_state(TaskChanges.new_due_date)

async def edit_task_due_date(message: types.Message, state: FSMContext):
    task_id = int((await state.get_data())["task_id"])
    start_date_str = (await state.get_data())["new_start_date"]
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y") 
    due_date_str = parse_and_validate_date(message.text, start_date)
    due_date = datetime.strptime(due_date_str, "%d.%m.%Y").date()
    user_id = message.from_user.id

    db = get_db_pool()
    async with db.acquire() as conn:
        task = await db.fetchrow("SELECT * FROM task WHERE id = $1", task_id)
        worker_id = task["task_assignee_id"]
        worker = await conn.fetchrow("SELECT * FROM users WHERE id = $1", worker_id)
        await db.execute("UPDATE task SET due_date = $1 WHERE id = $2", due_date, task_id)

    lang = await get_user_lang(user_id)
    text = {
        "en": f"The task \"{task['task_title']}\" due date has been changed to {due_date}",
        "ru": f"Дата завершения задачи \"{task['task_title']}\" была изменена на {due_date}",
        "uz": f"Vazifa \"{task['task_title']}\" tugash sanasi {due_date} ga o'zgartirildi"
    }

    await message.answer(text[lang])
    await bot.send_message(worker["user_id"], text[lang])
    await state.clear()
    await navigate_to_main_menu(user_id, message.chat.id, state)

async def edit_task_priority(callback: types.CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    last_button_message_id = message_data.get("main_menu_message_id")

    # Verify that the callback message is still active
    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return
    
    # Get the priority level from the callback data
    priority = callback.data.split('_')[-1]

    priority_id = await parse_priority_id(priority)

    # Update the task's priority level in the database
    user_id = callback.from_user.id
    db = get_db_pool()
    task_id = int((await state.get_data())["task_id"])
    task = await db.fetchrow("SELECT * FROM task WHERE id = $1", task_id)
    worker = await get_user(task["task_assignee_id"])
    await db.execute("UPDATE task SET priority = $1 WHERE id = $2", priority_id, task_id)

    # Prepare the keyboard and send a confirmation message in the user's language
    lang = await get_user_lang(user_id)
    
    text = {
        "en": f"The task with title: \"{task['task_title']}\n priority has been changed to {priority}",
        "ru": f"Приоритет задачи с названием: \"{task['task_title']}\" изменен на {priority}",
        "uz": f"Vazifa \"{task['task_title']}\" sarlavhasi {priority} ga o'zgartirildi"
    }

    await callback.message.edit_text(text[lang])
    await bot.send_message(worker["user_id"], text[lang])
    await state.clear()
    await navigate_to_main_menu(user_id, callback.message.chat.id, state)