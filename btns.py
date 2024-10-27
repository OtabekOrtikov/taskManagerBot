from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")],
        [
            InlineKeyboardButton(text="Моя компания", callback_data="company"),
            InlineKeyboardButton(text="Реферальные ссылки", callback_data="referral_links")
        ],
        [
            InlineKeyboardButton(text="Создать проект", callback_data="create_project"),
            InlineKeyboardButton(text="Настройки", callback_data="settings")
        ],
        [InlineKeyboardButton(text="Отчеты", callback_data="reports")]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Vazifa yaratish", callback_data="create_task")],
        [
            InlineKeyboardButton(text="Mening kompaniyam", callback_data="company"),
            InlineKeyboardButton(text="Referal havolalar", callback_data="referral_links")
        ],
        [
            InlineKeyboardButton(text="Loyiha yaratish", callback_data="create_project"),
            InlineKeyboardButton(text="Sozlamalar", callback_data="settings")
        ],
        [InlineKeyboardButton(text="Hisobotlar", callback_data="reports")]
    ]),
}

company_menu_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список отделов", callback_data="departments")],
        [InlineKeyboardButton(text="Список сотрудников", callback_data="list_workers")],
        [InlineKeyboardButton(text="Список задач", callback_data="show_company_tasks")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bo'limlar ro'yxati", callback_data="departments")],
        [InlineKeyboardButton(text="Xodimlar ro'yxati", callback_data="list_workers")],
        [InlineKeyboardButton(text="Vazifalar ro'yxati", callback_data="show_company_tasks")],
        [InlineKeyboardButton(text="Orqaga", callback_data="back_to_main_menu")]
    ]),
}

back_to_main = {
    "ru": InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu"),
    "uz": InlineKeyboardButton(text="Orqaga", callback_data="back_to_main_menu")
}

back_to_company = {
    "ru": InlineKeyboardButton(text="Назад", callback_data="company"),
    "uz": InlineKeyboardButton(text="Orqaga", callback_data="company")
}

back_page = {
    "ru": "⬅️ Назад",
    "uz": "⬅️ Orqaga"
}

next_page = {
    "ru": "Следующий ➡️",
    "uz": "Keyingi ➡️"
}