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

back_to_main = {
    "ru": InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu"),
    "uz": InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
}

company_menu_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список отделов", callback_data="departments")],
        [InlineKeyboardButton(text="Список сотрудников", callback_data="list_workers")],
        [InlineKeyboardButton(text="Список задач", callback_data="show_company_tasks")],
        [back_to_main["ru"]]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bo'limlar ro'yxati", callback_data="departments")],
        [InlineKeyboardButton(text="Xodimlar ro'yxati", callback_data="list_workers")],
        [InlineKeyboardButton(text="Vazifalar ro'yxati", callback_data="show_company_tasks")],
        [back_to_main["uz"]]
    ]),
}


back_to_company = {
    "ru": InlineKeyboardButton(text="⬅️ Назад", callback_data="company"),
    "uz": InlineKeyboardButton(text="⬅️ Orqaga", callback_data="company")
}

edit_user_info_btns = {
    "ru": [
        {"text": "Изменить имя", "callback_data": "edit_fullname"},
        {"text": "Изменить телефон", "callback_data": "edit_phone"},
        {"text": "Изменить дату рождения", "callback_data": "edit_birthdate"},
        {"text": "Изменить язык интерфейса", "callback_data": "edit_language"}
    ],
    "uz": [
        {"text": "Ismni o'zgartirish", "callback_data": "edit_fullname"},
        {"text": "Telefon raqamini o'zgartirish", "callback_data": "edit_phone"},
        {"text": "Tug'ilgan kunni o'zgartirish", "callback_data": "edit_birthdate"},    
        {"text": "Bot tili o'zgartirish", "callback_data": "edit_language"},\
    ]
}

back_to_settings = {
    "ru": {"text": "⬅️ Назад", "callback_data": "settings"},
    "uz": {"text": "⬅️ Orqaga", "callback_data": "settings"}
}

back_page = {
    "ru": "⬅️ Назад",
    "uz": "⬅️ Orqaga"
}

next_page = {
    "ru": "Следующий ➡️",
    "uz": "Keyingi ➡️"
}

settings_menu_btns = {
    "ru": InlineKeyboardButton(text="Изменить информацию", callback_data="edit_user_info"),
    "uz": InlineKeyboardButton(text="Ma'lumotlarni o'zgartirish", callback_data="edit_user_info")
}

company_info_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название компании", callback_data="edit_company_name")],
        [InlineKeyboardButton(text="Изменить отделы", callback_data="edit_departments")],
        [back_to_settings["ru"]]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kompaniya nomini o'zgartirish", callback_data="edit_company_name")],
        [InlineKeyboardButton(text="Bo'limlarni o'zgartirish", callback_data="edit_departments")],
        [back_to_settings["uz"]]
    ])
}

back_to_edit_company = {
    "ru": InlineKeyboardButton(text="⬅️ Назад", callback_data="change_company"),
    "uz": InlineKeyboardButton(text="⬅️ Orqaga", callback_data="change_company")
}