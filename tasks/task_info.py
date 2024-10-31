from aiogram.fsm.context import FSMContext
from btns import back_to_main
from database.db_utils import get_db_pool, get_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

from utils.parse_status import parse_status
from utils.priority_parser import parse_priority

async def task_info(callback: types.CallbackQuery, state: FSMContext):
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

    async with db.acquire() as conn:
        task = await conn.fetchrow("""
            SELECT
                t.id as task_id,
                t.task_title,
                t.task_description,
                t.start_date,
                t.due_date,
                t.status AS task_status,
                t.priority,
                p.project_name,
                o.fullname AS owner_fullname,
                o.user_id AS owner_user_id,
                o.phone_number AS owner_phone_number,
                u.fullname AS worker_fullname,
                u.user_id AS worker_user_id,
                u.phone_number AS worker_phone_number
            FROM 
                task t
            JOIN 
                users o ON t.task_owner_id = o.id
            JOIN 
                users u ON t.task_assignee_id = u.id
            LEFT JOIN
                project p ON p.id = t.project_id
            WHERE 
                t.id = $1;
""", task_id)
        owner_id = task['owner_user_id']
        worker_id = task['worker_user_id']
        status = await parse_status(task['task_status'], lang)

    task_text = {
        'en': f"""
Task: {task['task_title']}
Description: {task['task_description']}
Start date: {task['start_date']}
Due date: {task['due_date']}
Status: {status}
Priority: {await parse_priority(task['priority'], 'en')}
{f"Project: {task['project_name']}" if task['project_name'] else ""}
Created by: {task['owner_fullname']}
Creator phone number: {task['owner_phone_number']}
Designated person: {task['worker_fullname']}
Phone number: {task['worker_phone_number']}

{f"Started: {task.get('started_at')}" if task.get('started_at') else ""}
{f"Paused: {task.get('paused_at')}" if task.get('paused_at') else ""}
{f"Continued: {task.get('continued_at')}" if task.get('continued_at') else ""}
{f"Finished: {task.get('finished_at')}" if task.get('finished_at') else ""}
{f"Cancelled: {task.get('canceled_at')}" if task.get('cancelled_at') else ""}
""",
        'ru': f"""
Задача: {task['task_title']}
Описание: {task['task_description']}
Дата начала: {task['start_date']}
Дата завершения: {task['due_date']}
Статус: {status}
Приоритет: {await parse_priority(task['priority'], 'ru')}
{f"Проект: {task['project_name']}" if task['project_name'] else ""}
Создана: {task['owner_fullname']}
Телефон создателя: {task['owner_phone_number']}
Исполнитель: {task['worker_fullname']}
Телефон исполнителя: {task['worker_phone_number']}

{f"Начата: {task.get('started_at')}" if task.get('started_at') else ""}
{f"Приостановлена: {task.get('paused_at')}" if task.get('paused_at') else ""}
{f"Продолжена: {task.get('continued_at')}" if task.get('continued_at') else ""}
{f"Завершена: {task.get('finished_at')}" if task.get('finished_at') else ""}
{f"Отменена: {task.get('canceled_at')}" if task.get('cancelled_at') else ""}
""",
        'uz': f"""
Vazifa: {task['task_title']}
Tavsif: {task['task_description']}
Boshlanish sanasi: {task['start_date']}
Tugash sanasi: {task['due_date']}
Holat: {status}
Urg'anchilik: {await parse_priority(task['priority'], 'uz')}
{f"Proyekt: {task['project_name']}" if task['project_name'] else ""}
Yaratuvchi: {task['owner_fullname']}
Yaratuvchi telefon raqami: {task['owner_phone_number']}
Ijrochi: {task['worker_fullname']}
Ijrochi telefon raqami: {task['worker_phone_number']}

{f"Boshlandi: {task.get('started_at')}" if task.get('started_at') else ""}
{f"To‘xtatildi: {task.get('paused_at')}" if task.get('paused_at') else ""}
{f"Davom ettirildi: {task.get('continued_at')}" if task.get('continued_at') else ""}
{f"Yakunlandi: {task.get('finished_at')}" if task.get('finished_at') else ""}
{f"Bekor qilindi: {task.get('canceled_at')}" if task.get('cancelled_at') else ""}
"""
    }

    keyboard_text = {
        'worker': {
            'en': {
                'start': 'Start task',
                'pause': 'Pause task',
                'continue': 'Continue task',
                'finish': 'Finish task',
            },
            'ru': {
                'start': 'Начать задачу',
                'pause': 'Приостановить задачу',
                'continue': 'Продолжить задачу',
                'finish': 'Завершить задачу',
            },
            'uz': {
                'start': 'Vazifani boshlash',
                'pause': 'Vazifani to‘xtatish',
                'continue': 'Vazifani davom ettirish',
                'finish': 'Vazifani yakunlash',
            }
        },
        'owner': {
            'en': {
                'edit': 'Edit task',
                'delete': 'Delete task',
            },
            'ru': {
                'edit': 'Редактировать задачу',
                'delete': 'Удалить задачу',
            },
            'uz': {
                'edit': 'Vazifani tahrirlash',
                'delete': 'Vazifani o‘chirish',
            }
        }
    }
    
    keyboard = []

    if user_id == owner_id or user['role_id'] == 1:
        keyboard.append(
            [InlineKeyboardButton(text=keyboard_text['owner'][lang]['edit'], callback_data=f'edit_task_{task_id}')]
        )
        keyboard.append(
            [InlineKeyboardButton(text=keyboard_text['owner'][lang]['delete'], callback_data=f'cancel_task_{task_id}')]
        )
    elif user_id == worker_id:
        if status == 'Not started':
            keyboard.append([InlineKeyboardButton(text=keyboard_text['worker'][lang]['start'], callback_data=f'start_task_{task_id}')])
        elif status == 'In progress':
            keyboard.append([
                InlineKeyboardButton(text=keyboard_text['worker'][lang]['pause'], callback_data=f'pause_task_{task_id}'),
                InlineKeyboardButton(text=keyboard_text['worker'][lang]['finish'], callback_data=f'finish_task_{task_id}')
            ])
        elif status == 'Paused':
            keyboard.append([
                InlineKeyboardButton(text=keyboard_text['worker'][lang]['continue'], callback_data=f'continue_task_{task_id}'),
                InlineKeyboardButton(text=keyboard_text['worker'][lang]['finish'], callback_data=f'finish_task_{task_id}')
            ])
    keyboard.append([back_to_main[lang]])

    await callback.message.edit_text(task_text[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.update_data(main_menu_message_id=callback.message.message_id)