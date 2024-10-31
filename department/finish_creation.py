from aiogram.fsm.context import FSMContext
from config import BOT_USERNAME
from database.db_utils import get_user_lang, get_db_pool
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from menu.main_menu import navigate_to_main_menu

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
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company_id}_department={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Ребята, нажмите, пожалуйста, на ссылку, чтобы получить задачу от начальства."
            keyboard.append([InlineKeyboardButton(text=f"Отдел: {department['department_name']}", url=share_link)])
        await callback.message.edit_text("""
Теперь отправьте реферальную ссылку руководителю этого отдела. Он добавит всех участников этой группы или Вы сами можете добавить участников нажимая следующую кнопку с названием отдела. В кнопках указаны названия отделов.

P.s: Первый кто зайдет по этой ссылке будет руководителем. Но не переживай, в любой момент можете изменить должность сотрудников в настройках.""",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        for department in departments:
            referal_link = f"https://t.me/{BOT_USERNAME}?start={company_id}_department={department['id']}"
            share_link = f"https://t.me/share/url?url={referal_link}&text=Yigitlar, boshliqdan vazifa olish uchun quyidagi havolaga kiring."
            keyboard.append([InlineKeyboardButton(text=f"Bo'lim: {department['department_name']}", url=share_link)])
        await callback.message.edit_text("""
Endi bu bo‘lim rahbariga tavsiya havolani yuboring. U bu guruhdagi barcha a'zolarni qo‘shadi yoki siz o‘ziz qo‘shishingiz mumkin. Bo‘lim nomi tugmasini bosing.
                                         
P.s: Bu havolaga birinchi kiringan odam bo‘lib qoladi. Lekin xavotir bo‘lmang, har qanday vaqtda xodimlar vazifalarini sozlamalarda o‘zgartirishingiz mumkin.""")

    await navigate_to_main_menu(callback.from_user.id, callback.message.chat.id, state)