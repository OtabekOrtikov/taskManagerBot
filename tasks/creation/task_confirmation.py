from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from config import API_TOKEN
from database.db_utils import get_user, get_db_pool, create_task
from menu.main_menu import navigate_to_main_menu
from datetime import datetime

bot = Bot(token=API_TOKEN)

async def confirming_task(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()  # Await and store data once
    last_button_message_id = data.get("main_menu_message_id")

    if callback.message.message_id != last_button_message_id:
        await callback.answer("This button is no longer active.")
        return

    print("Task confirmation")
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user['lang']

    task_title = data.get("task_title")
    task_description = data.get("task_description")
    start_date_str = data.get("start_date")
    due_date_str = data.get("due_date")
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
    due_date = datetime.strptime(due_date_str, "%d.%m.%Y").date()
    task_owner_id = user['id']
    task_assignee_id = data.get("task_assignee_id")
    priority = data.get("priority")
    created_at = datetime.now().date()
    project_id = data.get("project_id") if data.get("project_id") else None

    db = get_db_pool()

    # Create the task
    await create_task(db, task_title, task_description, start_date, due_date, task_owner_id, task_assignee_id, priority, project_id, created_at)

    async with db.acquire() as connection:
        worker = await connection.fetchrow("SELECT * FROM users WHERE id = $1", task_assignee_id)
        if project_id:
            project = await connection.fetchrow("SELECT * FROM project WHERE id = $1", project_id)

    send_text = {
        'en': f"Task created successfully for {worker['fullname']} in the project {project['project_name']}." if project_id else f"Task created successfully for {worker['fullname']}.",
        'ru': f"Задача успешно создана для {worker['fullname']} в проекте {project['project_name']}." if project_id else f"Задача успешно создана для {worker['fullname']}.",
        'uz': f"Vazifa muvaffaqiyatli yaratildi {worker['fullname']} uchun {project['project_name']} proyektida." if project_id else f"Vazifa muvaffaqiyatli yaratildi {worker['fullname']} uchun."
    }

    notify_worker_text = {
        'en_company': f"You have a new task:\n\nTitle: {task_title}\nDescription: {task_description}\nStart date: {start_date}\nDue date: {due_date}\nPriority: {priority}\nCreated at: {created_at}\nCreated by: {user['fullname']}\n\nPlease check your tasks list.",
        'ru_company': f"У вас новая задача:\n\nНазвание: {task_title}\nОписание: {task_description}\nДата начала: {start_date}\nДата окончания: {due_date}\nПриоритет: {priority}\nСоздано: {created_at}\nСоздано: {user['fullname']}\n\nПожалуйста, проверьте свой список задач.",
        'uz_company': f"Sizga yangi vazifa berildi:\n\nSarlavha: {task_title}\nTavsif: {task_description}\nBoshlanish sanasi: {start_date}\nTugash sanasi: {due_date}\nUrg'atish: {priority}\nYaratilgan: {created_at}\nYaratuvchi: {user['fullname']}\n\nIltimos, vazifalar ro'yxatingizni tekshiring.",

        'en_project': f"You have a new task in the project {project['project_name']}:\n\nTitle: {task_title}\nDescription: {task_description}\nStart date: {start_date}\nDue date: {due_date}\nPriority: {priority}\nCreated at: {created_at}\nCreated by: {user['fullname']}\n\nPlease check your tasks list.",
        'ru_project': f"У вас новая задача в проекте {project['project_name']}:\n\nНазвание: {task_title}\nОписание: {task_description}\nДата начала: {start_date}\nДата окончания: {due_date}\nПриоритет: {priority}\nСоздано: {created_at}\nСоздано: {user['fullname']}\n\nПожалуйста, проверьте свой список задач.",
        'uz_project': f"Sizga {project['project_name']} proyektida yangi vazifa berildi:\n\nSarlavha: {task_title}\nTavsif: {task_description}\nBoshlanish sanasi: {start_date}\nTugash sanasi: {due_date}\nUrg'atish: {priority}\nYaratilgan: {created_at}\nYaratuvchi: {user['fullname']}\n\nIltimos, vazifalar ro'yxatingizni tekshiring."
    }


    # Send confirmation message and notify the assignee
    if lang == 'en':
        await callback.message.answer("Task created successfully. If you want to create another task, click the button below.")
        await bot.send_message(worker['user_id'], f"You have a new task:\n\nTitle: {task_title}\nDescription: {task_description}\nStart date: {start_date}\nDue date: {due_date}\nPriority: {priority}\nCreated at: {created_at}\nCreated by: {user['fullname']}\n\nPlease check your tasks list.")
    elif lang == 'ru':
        await callback.message.answer("Задача успешно создана. Если вы хотите создать еще одну задачу, нажмите кнопку ниже.")
        await bot.send_message(worker['user_id'], f"У вас новая задача:\n\nНазвание: {task_title}\nОписание: {task_description}\nДата начала: {start_date}\nДата окончания: {due_date}\nПриоритет: {priority}\nСоздано: {created_at}\nСоздано: {user['fullname']}\n\nПожалуйста, проверьте свой список задач.")
    elif lang == 'uz':
        await callback.message.answer("Vazifa muvaffaqiyatli yaratildi. Agar siz boshqa vazifa yaratmoqchi bo'lsangiz, pastdagi tugmani bosing.")
        await bot.send_message(worker['user_id'], f"Sizga yangi vazifa berildi:\n\nSarlavha: {task_title}\nTavsif: {task_description}\nBoshlanish sanasi: {start_date}\nTugash sanasi: {due_date}\nUrg'atish: {priority}\nYaratilgan: {created_at}\nYaratuvchi: {user['fullname']}\n\nIltimos, vazifalar ro'yxatingizni tekshiring.")
    
    await callback.message.answer(send_text[lang])
    await bot.send_message(worker['user_id'], notify_worker_text[f"{lang}_{"project" if project_id else "company"}"])
    await state.clear()
    await callback.message.delete_reply_markup()
    await navigate_to_main_menu(user_id, callback.message.chat.id, state)
