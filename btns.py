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
    "en": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Create task", callback_data="create_task")],
        [
            InlineKeyboardButton(text="My company", callback_data="company"),
            InlineKeyboardButton(text="Referral links", callback_data="referral_links")
        ],
        [
            InlineKeyboardButton(text="Create project", callback_data="create_project"),
            InlineKeyboardButton(text="Settings", callback_data="settings")
        ],
        [InlineKeyboardButton(text="Reports", callback_data="reports")]
    ])
}

back_to_main = {
    "ru": InlineKeyboardButton(text="🔙Назад", callback_data="back_to_main_menu"),
    "uz": InlineKeyboardButton(text="🔙Orqaga", callback_data="back_to_main_menu"),
    "en": InlineKeyboardButton(text="🔙Back", callback_data="back_to_main_menu")
}

company_menu_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список отделов", callback_data="departments")],
        [InlineKeyboardButton(text="Список сотрудников", callback_data="list_workers")],
        [InlineKeyboardButton(text="Список задач", callback_data="show_company_tasks")],
        [InlineKeyboardButton(text="Список проектов", callback_data="show_company_projects")],
        [back_to_main["ru"]]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bo'limlar ro'yxati", callback_data="departments")],
        [InlineKeyboardButton(text="Xodimlar ro'yxati", callback_data="list_workers")],
        [InlineKeyboardButton(text="Vazifalar ro'yxati", callback_data="show_company_tasks")],
        [InlineKeyboardButton(text="Loyihalar ro'yxati", callback_data="show_company_projects")],
        [back_to_main["uz"]]
    ]),
    "en": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Departments list", callback_data="departments")],
        [InlineKeyboardButton(text="Workers list", callback_data="list_workers")],
        [InlineKeyboardButton(text="Tasks list", callback_data="show_company_tasks")],\
        [InlineKeyboardButton(text="Projects list", callback_data="show_company_projects")],
        [back_to_main["en"]]
    ])
}


back_to_company = {
    "ru": InlineKeyboardButton(text="🔙Назад", callback_data="company"),
    "uz": InlineKeyboardButton(text="🔙Orqaga", callback_data="company"),
    "en": InlineKeyboardButton(text="🔙Back", callback_data="company")
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
        {"text": "Bot tili o'zgartirish", "callback_data": "edit_language"},
    ],
    "en": [
        {"text": "Change name", "callback_data": "edit_fullname"},
        {"text": "Change phone number", "callback_data": "edit_phone"},
        {"text": "Change birthdate", "callback_data": "edit_birthdate"},
        {"text": "Change interface language", "callback_data": "edit_language"}
    ]
}

back_to_settings = {
    "ru": {"text": "🔙Назад", "callback_data": "settings"},
    "uz": {"text": "🔙Orqaga", "callback_data": "settings"},
    "en": {"text": "🔙Back", "callback_data": "settings"}
}

back_page = {
    "ru": "🔙Назад",
    "uz": "🔙Orqaga",
    "en": "🔙Back"
}

next_page = {
    "ru": "Следующий ➡️",
    "uz": "Keyingi ➡️",
    "en": "Next ➡️"
}

settings_menu_btns = {
    "ru": InlineKeyboardButton(text="Изменить информацию", callback_data="edit_user_info"),
    "uz": InlineKeyboardButton(text="Ma'lumotlarni o'zgartirish", callback_data="edit_user_info"),
    "en": InlineKeyboardButton(text="Edit information", callback_data="edit_user_info")
}

company_info_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название компании", callback_data="edit_company_name")],
        [InlineKeyboardButton(text="Изменить отделы", callback_data="edit_departments")],
        [InlineKeyboardButton(text="Управление сотрудниками", callback_data="control_workers")],
        [back_to_settings["ru"]]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kompaniya nomini o'zgartirish", callback_data="edit_company_name")],
        [InlineKeyboardButton(text="Bo'limlarni o'zgartirish", callback_data="edit_departments")],
        [InlineKeyboardButton(text="Управление сотрудниками", callback_data="control_workers")],
        [back_to_settings["uz"]]
    ]),
    "en": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Change company name", callback_data="edit_company_name")],
        [InlineKeyboardButton(text="Change departments", callback_data="edit_departments")],
        [InlineKeyboardButton(text="Manage workers", callback_data="control_workers")],
        [back_to_settings["en"]]
    ])
}

back_to_edit_company = {
    "ru": InlineKeyboardButton(text="🔙Назад", callback_data="change_company"),
    "uz": InlineKeyboardButton(text="🔙Orqaga", callback_data="change_company"),
    "en": InlineKeyboardButton(text="🔙Back", callback_data="change_company")
}

priority_btns = {
    "ru": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Низкий", callback_data="task_priority_1"),
         InlineKeyboardButton(text="Средний", callback_data="task_priority_2"),
         InlineKeyboardButton(text="Высокий", callback_data="task_priority_3")],
        [back_to_main["ru"]]
    ]),
    "uz": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Past", callback_data="task_priority_1"),
         InlineKeyboardButton(text="O'rta", callback_data="task_priority_2"),
         InlineKeyboardButton(text="Yuqori", callback_data="task_priority_3")],
        [back_to_main["uz"]]
    ]),
    "en": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Low", callback_data="task_priority_1"),
         InlineKeyboardButton(text="Medium", callback_data="task_priority_2"),
         InlineKeyboardButton(text="High", callback_data="task_priority_3")],
        [back_to_main["en"]]
    ])
}