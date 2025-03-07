from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_btn = [
    [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"), 
     InlineKeyboardButton(text="🇺🇿 Ўзбекча", callback_data="lang_oz"), 
     InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
]

main_menu_btn = {
    "ru": [
        [InlineKeyboardButton(text="⬇️ Взять долг", callback_data="get_debt")],
        [InlineKeyboardButton(text="⬆️ Отдать долг", callback_data="give_debt")],
        [InlineKeyboardButton(text="📗 Список выданных долгов", callback_data="given_debts"),
         InlineKeyboardButton(text="📕 Список полученных долгов", callback_data="taken_debts")],
        [InlineKeyboardButton(text="👥 Список людей", callback_data="people_list"),
         InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        #  [InlineKeyboardButton(text="B2B", callback_data="b2b")],
    ],
    "uz": [
        [InlineKeyboardButton(text="⬇️ Qarz olish", callback_data="get_debt")],
        [InlineKeyboardButton(text="⬆️ Qarz berish", callback_data="give_debt")],
        [InlineKeyboardButton(text="📗 Berilgan qarzlar ro'yxati", callback_data="given_debts"),
         InlineKeyboardButton(text="📕 Olingan qarzlar ro'yxati", callback_data="taken_debts")],
        [InlineKeyboardButton(text="👥 Odamlar ro'yxati", callback_data="people_list"),
         InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        #  [InlineKeyboardButton(text="B2B", callback_data="b2b")],
    ],
    "oz": [
        [InlineKeyboardButton(text="⬇️ Қарз олиш", callback_data="get_debt")],
        [InlineKeyboardButton(text="⬆️ Қарз бериш", callback_data="give_debt")],
        [InlineKeyboardButton(text="📗 Берилган қарзлар рўйхати", callback_data="given_debts"),
         InlineKeyboardButton(text="📕 Олинган қарзлар рўйхати", callback_data="taken_debts")],
        [InlineKeyboardButton(text="👥 Одамлар рўйхати", callback_data="people_list"),
         InlineKeyboardButton(text="⚙️ Созламалар", callback_data="settings")],
        #  [InlineKeyboardButton(text="B2B", callback_data="b2b")],
    ]
}

back_btn = {
    "ru": InlineKeyboardButton(text="🔙Назад в главное меню", callback_data="back"),
    "uz": InlineKeyboardButton(text="🔙Asosiy menyuga qaytish", callback_data="back"),
    "oz": InlineKeyboardButton(text="🔙Асосий менюга қайтиш", callback_data="back"),
}

currency_btn = {
    "get": [
        [InlineKeyboardButton(text="💵USD", callback_data="getdebt_currency_usd"),
         InlineKeyboardButton(text="💶EUR", callback_data="getdebt_currency_eur")],
        [InlineKeyboardButton(text="💸RUB", callback_data="getdebt_currency_rub"),
         InlineKeyboardButton(text="💰UZS", callback_data="getdebt_currency_uzs")],
    ],
    "give": [
        [InlineKeyboardButton(text="💵USD", callback_data="givedebt_currency_usd"),
         InlineKeyboardButton(text="💶EUR", callback_data="givedebt_currency_eur")],
        [InlineKeyboardButton(text="💸RUB", callback_data="givedebt_currency_rub"),
         InlineKeyboardButton(text="💰UZS", callback_data="givedebt_currency_uzs")],
    ]
}

set_today_btn = {
    "get": {
        "ru": InlineKeyboardButton(text="📆Установить сегодня", callback_data="set_today_getdebt"),
        "uz": InlineKeyboardButton(text="📆Бугунни ўрнатиш", callback_data="set_today_getdebt"),
        "oz": InlineKeyboardButton(text="📆Бугунни ўрнатиш", callback_data="set_today_getdebt"),
    },
    "give": {
        "ru": InlineKeyboardButton(text="📆Установить сегодня", callback_data="set_today_givedebt"),
        "uz": InlineKeyboardButton(text="📆Бугунни ўрнатиш", callback_data="set_today_givedebt"),
        "oz": InlineKeyboardButton(text="📆Бугунни ўрнатиш", callback_data="set_today_givedebt"),
    }
}

divide_btn = {
    "ru": [
        [InlineKeyboardButton(text="1️⃣ месяц", callback_data="getdebt_divide_1"),
         InlineKeyboardButton(text="3️⃣ месяца", callback_data="getdebt_divide_3")],
        [InlineKeyboardButton(text="6️⃣ месяцев", callback_data="getdebt_divide_6"),
         InlineKeyboardButton(text="1️⃣2️⃣ месяцев", callback_data="getdebt_divide_12")],
        [back_btn['ru']]
    ],
    "uz": [
        [InlineKeyboardButton(text="1️⃣ месяц", callback_data="getdebt_divide_1"),
         InlineKeyboardButton(text="3️⃣ месяца", callback_data="getdebt_divide_3")],
        [InlineKeyboardButton(text="6️⃣ месяцев", callback_data="getdebt_divide_6"),
         InlineKeyboardButton(text="1️⃣2️⃣ месяцев", callback_data="getdebt_divide_12")],
        [back_btn['uz']]
    ],
    "oz": [
        [InlineKeyboardButton(text="1️⃣ месяц", callback_data="getdebt_divide_1"),
         InlineKeyboardButton(text="3️⃣ месяца", callback_data="getdebt_divide_3")],
        [InlineKeyboardButton(text="6️⃣ месяцев", callback_data="getdebt_divide_6"),
         InlineKeyboardButton(text="1️⃣2️⃣ месяцев", callback_data="getdebt_divide_12")],
        [back_btn['oz']]
    ]
}

filter_btn = {
    "ru": InlineKeyboardButton(text="⚙️ Настройка фильтрации", callback_data="filter_settings"),
    "uz": InlineKeyboardButton(text="⚙️ Filter sozlamalari", callback_data="filter_settings"),
    "oz": InlineKeyboardButton(text="⚙️ Фильтер созламалари", callback_data="filter_settings")
}

user_change_btn = {
    "ru": [
        [InlineKeyboardButton(text="👤 Изменить имя", callback_data="changedata_name")],
        [InlineKeyboardButton(text="📞 Изменить номер", callback_data="changedata_phone")],
        [InlineKeyboardButton(text="🎂 Изменить дату рождения", callback_data="changedata_birthday")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
    ],
    "uz": [
        [InlineKeyboardButton(text="👤 Ismni o'zgartirish", callback_data="changedata_name")],
        [InlineKeyboardButton(text="📞 Raqamni o'zgartirish", callback_data="changedata_phone")],
        [InlineKeyboardButton(text="🎂 Tug'ilgan kunni o'zgartirish", callback_data="changedata_birthday")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings")]
    ],
    "oz": [
        [InlineKeyboardButton(text="👤 Исмни ўзгартириш", callback_data="changedata_name")],
        [InlineKeyboardButton(text="📞 Рақамни ўзгартириш", callback_data="changedata_phone")],
        [InlineKeyboardButton(text="🎂 Туғилган кунни ўзгартириш", callback_data="changedata_birthday")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="settings")]
    ]
}

# Filter entry button (the "Filter" button in the main list)
filter_btn = {
    "ru": [InlineKeyboardButton(text="Фильтр", callback_data="filter_settings")],
    "uz": [InlineKeyboardButton(text="Filtrlash", callback_data="filter_settings")],
    "oz": [InlineKeyboardButton(text="Филтрлаш", callback_data="filter_settings")]
}

back_btn = {
    "ru": InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
    "uz": InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
    "oz": InlineKeyboardButton(text="🔙 Орқага", callback_data="back")
}

filter_settings_btn = {
    "ru": [
        [InlineKeyboardButton(text="📅 Дата", callback_data="filter_date")],
        [InlineKeyboardButton(text="🔴 Статус", callback_data="filter_status")],
        [InlineKeyboardButton(text="💰 Валюта", callback_data="filter_currency")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ],
    "uz": [
        [InlineKeyboardButton(text="📅 Sana", callback_data="filter_date")],
        [InlineKeyboardButton(text="🔴 Status", callback_data="filter_status")],
        [InlineKeyboardButton(text="💰 Valyuta", callback_data="filter_currency")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
    ],
    "oz": [
        [InlineKeyboardButton(text="📅 Сана", callback_data="filter_date")],
        [InlineKeyboardButton(text="🔴 Статус", callback_data="filter_status")],
        [InlineKeyboardButton(text="💰 Валюта", callback_data="filter_currency")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back")]
    ]
}

filter_date_btn = {
    "ru": [
        [InlineKeyboardButton(text="📅 Показать новые", callback_data="filter_date_new")],
        [InlineKeyboardButton(text="📅 Показать старые", callback_data="filter_date_old")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="filter_settings")]
    ],
    "uz": [
        [InlineKeyboardButton(text="📅 Yangilarini ko'rsatish", callback_data="filter_date_new")],
        [InlineKeyboardButton(text="📅 Eskilarini ko'rsatish", callback_data="filter_date_old")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="filter_settings")]
    ],
    "oz": [
        [InlineKeyboardButton(text="📅 Янгиларини кўрсатиш", callback_data="filter_date_new")],
        [InlineKeyboardButton(text="📅 Ескиларини кўрсатиш", callback_data="filter_date_old")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="filter_settings")]
    ]
}

filter_currency_btn = {
    "ru": [
        [InlineKeyboardButton(text="💵 USD", callback_data="filter_currency_usd")],
        [InlineKeyboardButton(text="💶 EUR", callback_data="filter_currency_eur")],
        [InlineKeyboardButton(text="💸 RUB", callback_data="filter_currency_rub")],
        [InlineKeyboardButton(text="💰 UZS", callback_data="filter_currency_uzs")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="filter_settings")]
    ],
    "uz": [
        [InlineKeyboardButton(text="💵 USD", callback_data="filter_currency_usd")],
        [InlineKeyboardButton(text="💶 EUR", callback_data="filter_currency_eur")],
        [InlineKeyboardButton(text="💸 RUB", callback_data="filter_currency_rub")],
        [InlineKeyboardButton(text="💰 UZS", callback_data="filter_currency_uzs")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="filter_settings")]
    ],
    "oz": [
        [InlineKeyboardButton(text="💵 USD", callback_data="filter_currency_usd")],
        [InlineKeyboardButton(text="💶 EUR", callback_data="filter_currency_eur")],
        [InlineKeyboardButton(text="💸 RUB", callback_data="filter_currency_rub")],
        [InlineKeyboardButton(text="💰 UZS", callback_data="filter_currency_uzs")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="filter_settings")]
    ]
}

filter_status_btn = {
    "ru": [
        [InlineKeyboardButton(text="🔴 Просроченные", callback_data="filter_status_overdue")],
        [InlineKeyboardButton(text="🟡 Не закрытые", callback_data="filter_status_active")],
        [InlineKeyboardButton(text="🟢 Погашенные", callback_data="filter_status_completed")],
        [InlineKeyboardButton(text="🟠 Черновики", callback_data="filter_status_draft")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="filter_settings")]
    ],
    "uz": [
        [InlineKeyboardButton(text="🔴 O'tkazib yuborilgan", callback_data="filter_status_overdue")],
        [InlineKeyboardButton(text="🟡 To'lanmagan", callback_data="filter_status_active")],
        [InlineKeyboardButton(text="🟢 To'langan", callback_data="filter_status_completed")],
        [InlineKeyboardButton(text="🟠 Qoralama", callback_data="filter_status_draft")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="filter_settings")]
    ],
    "oz": [
        [InlineKeyboardButton(text="🔴 Ўтказиб юборилган", callback_data="filter_status_overdue")],
        [InlineKeyboardButton(text="🟡 Тўланмаган", callback_data="filter_status_active")],
        [InlineKeyboardButton(text="🟢 Тўланган", callback_data="filter_status_completed")],
        [InlineKeyboardButton(text="🟠 Қоралама", callback_data="filter_status_draft")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="filter_settings")]
    ]
}
