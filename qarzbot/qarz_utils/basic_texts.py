from datetime import datetime
import json
from qarz_database.db_utils import get_user_by_id

noactive_btn = {
    "ru": "Эта кнопка не активна.",
    "uz": "Bu tugma faol emas.",
    "уз": "Бу тугма фаол эмас."
}

missing_field = {
    "ru": {
        "basic": "❗️Вы пропустили некоторые поля. Пожалуйста, заполните их.",
        "fullname": "❗️Напишите пожалуйста ваше имя и фамилию.",
        "phone_number": "❗️Напишите или нажмите кнопки ниже, чтобы отправить ваш номер телефона.",
        "birthdate": "📅Напиши ваше дату рождение в формате 'ДД.ММ.ГГГГ'.",
        "rules": "📚Вы не прочитали и не приняли правила бота."
    },
    "uz": {
        "basic": "❗️Siz ba'zi maydonlarni o'tkazdingiz. Iltimos, ularni to'ldiring.",
        "fullname": "❗️Iltimos, ism va familiyangizni yozing.",
        "phone_number": "❗️Iltimos, telefon raqamingizni yozing yoki tugmani bosing.",
        "birthdate": "📅Sana yozing 'КК.ОО.ЙЙЙЙ' formatida.",
        "rules": "📚Siz bot qoidalarni o'qimadingiz va qabul qilmadingiz."
    },
    "oz": {
        "basic": "❗️Сиз баъзи майдонларни ўтказдингиз. Илтимос, уларни тўлдиринг.",
        "fullname": "❗️Илтимос, исм ва фамилиянгизни ёзинг.",
        "phone_number": "❗️Илтимос, телефон рақамингизни ёзинг ёки тугмани босинг.",
        "birthdate": "📅Сана ёзинг 'КК.ОО.ЙЙЙЙ' форматида.",
        "rules": "📚Сиз бот қоидаларни ўқимадингиз ва қабул қилмадингиз."
    }
}

invalid_referal = {
    "ru": "❗️Неверные параметры реферальной ссылки. Пожалуйста, проверьте ссылку.",
    "uz": "❗️Noto'g'ri referal havolasi parametrlari. Iltimos, havolani tekshiring.",
    "уз": "❗️Нотўғри реферал ҳаволаси параметрлари. Илтимос, ҳаволани текширинг."
}

welcome_text = """
👋🏻Здравствуйте! Я - бот для управления долгами. Я помогу вам вести учет долгов.
Чтобы начать работу, вам нужно зарегистрироваться. Для начала выберите язык интерфейса.

===========================================

👋🏻Assalomu aleykum! Men qarzlar boshqarish uchun botman. Qarzlar hisobini yuritishda yordam beraman.
Ishni boshlash uchun ro'yxatdan o'tishingiz kerak. Boshlash uchun interfeys tilini tanlang."""

registrated_text = {
    "ru": "Вы уже зарегистрированы.",
    "uz": "Siz allaqachon ro'yxatdan o'tgansiz.",
    "уз": "Сиз аллақачон рўйхатдан ўтгансиз."
}

invalid_birthdate = {
    "ru": "❗️Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ",
    "uz": "❗️Noto'g'ri sana formati. Iltimos, sanani KK.OO.YYYY formatda kiriting",
    "уз": "❗️Нотўғри сана формати. Илтимос, санани КК.ОО.ЙЙЙЙ форматда киритинг"
}

invalid_phone = {
    "ru": "❗Номер телефона введен неверно. Пожалуйста, введите номер в формате +998XXXXXXXXX",
    "uz": "❗Telefon raqami noto'g'ri kiritildi. Iltimos, telefon raqamini +998XXXXXXXXX formatda kiriting",
    "oz": "❗Телефон рақами нотўғри киритилди. Илтимос, телефон рақамини +998XXXXXXXXX форматда киритинг"
}

invalid_creditor = {
    "ru": "❗Неверный формат имени должника. Пожалуйста, введите имя должника.",
    "uz": "❗Qarzdor ismi noto'g'ri formatda. Iltimos, qarzdor ismini kiriting.",
    "oz": "❗Қарздор исми нотўғри форматда. Илтимос, қарздор исмини киритинг."
}

invalid_d_p_format = {
    "ru": "❗Неверный формат ввода. Пожалуйста, введите имя должника и его номер телефона в формате 'Имя - +998XXXXXXXXX'",
    "uz": "❗Noto'g'ri kiritish formati. Iltimos, qarzdor ismini va uning telefon raqamini 'Ism - +998XXXXXXXXX' formatda kiriting",
    "oz": "❗Нотўғри киритиш формати. Илтимос, қарздор исмини ва унинг телефон рақамини 'Исм - +998XXXXXXXXX' форматда киритинг"
}

invalid_amount = {
    "ru": "❗Неверный формат ввода. Пожалуйста, введите сумму долга.",
    "uz": "❗Noto'g'ri kiritish formati. Iltimos, qarz summasini kiriting.",
    "oz": "❗Нотўғри киритиш формати. Илтимос, қарз суммасини киритинг."
}

invalid_date = {
    "ru": "❗Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ",
    "uz": "❗Noto'g'ri sana formati. Iltimos, sanani KK.OO.YYYY formatda kiriting",
    "oz": "❗Нотўғри сана формати. Илтимос, санани КК.ОО.ЙЙЙЙ форматда киритинг"
}

rules_text = {
    "ru": "📚Правила",
    "uz": "📚Qoidalar",
    "oz": "📚Қоидалар"
}
rules_links = {
    "ru": "https://telegra.ph/Pravila-zajma-11-20",
    "uz": "https://telegra.ph/Qarz-oldi-berdi-munosabatlari-uchun-eslatma-11-20",
    "oz": "https://telegra.ph/%D2%9Aarz-oldi-berdi-%D2%9Boidalari-11-20"
}
accept_text = {
    "ru": "☑️Принять правила",
    "uz": "☑️Qoidalar qabul qilish",
    "oz": "☑️Қоидаларни қабул қилиш"
}

registration_complete = {
    "ru": "🎉Регистрация завершена!",
    "uz": "🎉Ro'yxatdan o'tish yakunlandi!",
    "oz": "🎉Рўйхатдан ўтиш якунланди!"
}

next_page_text = {
    "ru": "Следующая страница➡️",
    "uz": "Keyingi sahifa➡️",
    "oz": "Кейинги саҳифа➡️"
}

previous_page_text = {
    "ru": "⬅️Предыдущая страница",
    "uz": "⬅️Oldingi sahifa",
    "oz": "⬅️Олдинги саҳифа"
}

skip_text = {
    "ru": "Пропустить➡️",
    "uz": "O'tkazib yuborish➡️",
    "oz": "Ўтказиб юбориш➡️"
}

end_text = {
    "ru": "✋Завершить",
    "uz": "✋Yakunlash",
    "oz": "✋Якунлаш"
}

debt_404 = {
    "ru": "❗️Долг не найден.",
    "uz": "❗️Qarz topilmadi.",
    "oz": "❗️Қарз топилмади."
}

back_text = {
    "ru": "🔙 Назад",
    "uz": "🔙 Orqaga",
    "oz": "🔙 Орқага"
}

currency_parse = {
    "uzs": {
        "ru": "сум",
        "uz": "so'm",
        "oz": "сўм",
        "symbol": "UZS"
    },
    "usd": {
        "ru": "доллар",
        "uz": "dollar",
        "oz": "доллар",
        "symbol": "$"
    },
    "rub": {
        "ru": "рубль",
        "uz": "rubl",
        "oz": "рубль",
        "symbol": "₽"
    },
    "eur": {
        "ru": "евро",
        "uz": "yevro",
        "oz": "евро",
        "symbol": "€"
    },
}

status_parse = {
    "active": {
        "ru": {
            "full": "🟡 Не закрытый долг",
            "short": "🟡"
        },
        "uz": {
            "full": "🟡 Тўланмаган қарз",
            "short": "🟡"
        },
        "oz": {
            "full": "🟡 To'lanmagan qarz",
            "short": "🟡"
        }
    },
    "closed": {
        "ru": {
            "full": "🟢 Закрытый долг",
            "short": "🟢"
        },
        "uz": {
            "full": "🟢 Тўланган қарз",
            "short": "🟢"
        },
        "oz": {
            "full": "🟢 To'langan qarz",
            "short": "🟢"
        }
    },
    "overdue": {
        "ru": {
            "full": "🔴 Просроченный долг",
            "short": "🔴"
        },
        "uz": {
            "full": "🔴 Muddati o'tgan qarz",
            "short": "🔴"
        },
        "oz": {
            "full": "🔴 Муддати ўтган қарз",
            "short": "🔴"
        }
    },
    "draft": {
        "ru": {
            "full": "🟠 Черновик",
            "short": "🟠"
        },
        "uz": {
            "full": "🟠 Qoralama",
            "short": "🟠"
        },
        "oz": {
            "full": "🟠 Qoralama",
            "short": "🟠"
        }
    }
}

no_comment = {
    "ru": "Без комментария",
    "uz": "Izohsiz",
    "oz": "Изоҳсиз"
}

async def borrower_debt_text(debt):
    # Parse `due_date` and `amounts` if they are strings
    try:
        due_dates = json.loads(debt['due_date']) if isinstance(debt['due_date'], str) else debt['due_date']
        amounts = json.loads(debt['amounts']) if isinstance(debt['amounts'], str) else debt['amounts']
    except json.JSONDecodeError:
        raise ValueError("Failed to parse due dates or amounts as JSON.")

    # Ensure lengths of `due_dates` and `amounts` match
    if not isinstance(due_dates, list) or not isinstance(amounts, list):
        raise ValueError("due_date and amounts must be qarz_lists.")
    if len(due_dates) != len(amounts):
        raise ValueError("Mismatch between number of due dates and amounts.")

    # Format due dates and amounts into text
    due_date_texts = [
        f"{date} - {amount} {currency_parse[debt['currency']]['symbol']}"
        for date, amount in zip(due_dates, amounts)
    ]
    due_dates_display = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(due_date_texts)])

    borrower = await get_user_by_id(debt['borrower_id'])

    return {
        "ru": (
            f"От Вас хотят взять долг.\n📑 Информация о долге:\n\n"
            f"👤Имя заёмщика: {debt['draft_name']}\n"
            f"📞Номер заёмщика: {debt['draft_phone']}\n"
            f"👤Имя должника: {borrower['fullname']}\n"
            f"📞Номер должника: {borrower['phone_number']}\n"
            f"💸Сумма долга: {debt['full_amount']} {currency_parse[debt['currency']]['ru']}\n"
            f"📅Дата получение долга: {debt['loan_date']}\n"
            f"📅График платежей:\n{due_dates_display}\n"
            f"💬Комментарий: {debt['comment'] if debt['comment'] else 'без комментария'}\n\n"
            f"📝Нажмите кнопку ниже, чтобы принять или отклонить запрос."
        ),
        "uz": (
            f"Sizdan qarz so'rayapti.\n📑Qarz haqida ma'lumot:\n\n"
            f"👤Qarz oluvchi ismi: {debt['draft_name']}\n"
            f"📞Qarz oluvchi raqami: {debt['draft_phone']}\n"
            f"👤Qarzdor ismi: {borrower['fullname']}\n"
            f"📞Qarzdor raqami: {borrower['phone_number']}\n"
            f"💸Qarz summasi: {debt['full_amount']} {currency_parse[debt['currency']]['uz']}\n"
            f"📅Qarz olish sanasi: {debt['loan_date']}\n"
            f"📅To'lovlar jadvali:\n{due_dates_display}\n"
            f"💬Izoh: {debt['comment'] if debt['comment'] else 'izohsiz'}\n\n"
            f"📝So'rovni qabul yoki rad etish uchun pastdagi tugmani bosing."
        ),
        "oz": (
            f"Сиздан қарз сўрайапти.\n📑Қарз ҳақида маълумот:\n\n"
            f"👤Исм олувчи: {debt['draft_name']}\n"
            f"📞Телефон рақами: {debt['draft_phone']}\n"
            f"👤Борчи исми: {borrower['fullname']}\n"
            f"📞Борчи рақами: {borrower['phone_number']}\n"
            f"💸Қарз суммаси: {debt['full_amount']} {currency_parse[debt['currency']]['oz']}\n"
            f"📅Қарз олиш санаси: {debt['loan_date']}\n"
            f"📅Тўловлар жадвали:\n{due_dates_display}\n"
            f"💬Изоҳ: {debt['comment'] if debt['comment'] else 'изоҳсиз'}\n\n"
            f"📝Сўровни қабул ёки рад этиш учун тугмани босинг."
        )
    }

async def debtor_debt_text(debt, user):
    """Generate debt confirmation text for the debtor."""
    try:
        # Safely parse due_date and amounts
        due_dates = json.loads(debt['due_date']) if isinstance(debt['due_date'], str) else debt['due_date'] or []
        amounts = json.loads(debt['amounts']) if isinstance(debt['amounts'], str) else debt['amounts'] or []
    except json.JSONDecodeError:
        raise ValueError("Failed to parse due dates or amounts as JSON.")

    if not isinstance(due_dates, list) or not isinstance(amounts, list):
        raise ValueError("due_date and amounts must be qarz_lists.")
    if len(due_dates) != len(amounts):
        raise ValueError("Mismatch between number of due dates and amounts.")

    # Format due dates and amounts
    due_date_texts = [
        f"{date} - {amount} {currency_parse[debt['currency']]['symbol']}"
        for date, amount in zip(due_dates, amounts)
    ]
    due_dates_display = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(due_date_texts)])

    debtor = await get_user_by_id(debt['debtor_id'])
    if not debtor:
        raise ValueError("Debtor not found.")  # Ensure debtor exists

    return {
        "ru": (
            f"Вы хотите взять долг.\n📑 Информация о долге:\n\n"
            f"👤Имя заёмщика: {user['fullname']}\n"
            f"📞Номер заёмщика: {user['phone_number']}\n"
            f"👤Имя должника: {debtor['fullname']}\n"
            f"📞Номер должника: {debtor['phone_number']}\n"
            f"💸Сумма долга: {debt['full_amount']} {currency_parse[debt['currency']]['ru']}\n"
            f"📅Дата получения долга: {debt['loan_date']}\n"
            f"📅График платежей:\n{due_dates_display}\n"
            f"💬Комментарий: {debt['comment'] if debt['comment'] else 'без комментария'}\n\n"
            f"📝Нажмите кнопку ниже, чтобы принять или отклонить запрос."
        ),
        "uz": (
            f"Siz qarz olmoqchisiz.\n📑Qarz haqida ma'lumot:\n\n"
            f"👤Qarz beruvchi ismi: {user['fullname']}\n"
            f"📞Qarz beruvchi raqami: {user['phone_number']}\n"
            f"👤Qarzdor ismi: {debtor['fullname']}\n"
            f"📞Qarzdor raqami: {debtor['phone_number']}\n"
            f"💸Qarz summasi: {debt['full_amount']} {currency_parse[debt['currency']]['uz']}\n"
            f"📅Qarz olish sanasi: {debt['loan_date']}\n"
            f"📅To'lovlar jadvali:\n{due_dates_display}\n"
            f"💬Izoh: {debt['comment'] if debt['comment'] else 'izohsiz'}\n\n"
            f"📝So'rovni qabul yoki rad etish uchun pastdagi tugmani bosing."
        ),
        "oz": (
            f"Сиз қарз олмоқчисиз.\n📑Қарз ҳақида маълумот:\n\n"
            f"👤Қарз берувчи исми: {user['fullname']}\n"
            f"📞Қарз берувчи рақами: {user['phone_number']}\n"
            f"👤Қарздор исми: {debtor['fullname']}\n"
            f"📞Қарздор рақами: {debtor['phone_number']}\n"
            f"💸Қарз суммаси: {debt['full_amount']} {currency_parse[debt['currency']]['oz']}\n"
            f"📅Қарз олиш санаси: {debt['loan_date']}\n"
            f"📅Тўловлар жадвали:\n{due_dates_display}\n"
            f"💬Изоҳ: {debt['comment'] if debt['comment'] else 'изоҳсиз'}\n\n"
            f"📝Сўровни қабул ёки рад этиш учун тугмани босинг."
        )
    }


def creation_getdebt_text(user, data, comment=""):
    creditor_name = data.get("getdebt_creditor")
    creditor_phone_number = data.get("getdebt_creditor_phone")
    amount = int(data.get("getdebt_amount"))
    currency = data.get("getdebt_currency")
    loan_date = datetime.strptime(data.get("getdebt_loan_date"), "%d.%m.%Y")

    # Parse due dates and divided amounts
    due_dates = [
        datetime.strptime(item["due_date"], "%d.%m.%Y").strftime("%d.%m.%Y")
        for item in data.get("getdebt_due_date", [])
    ]
    divided_amounts = [
        int(item["divided_amount"])
        for item in data.get("getdebt_amounts", [])
    ]

    # Ensure due_dates and divided_amounts have the same length
    if len(due_dates) != len(divided_amounts):
        raise ValueError("Mismatch between due dates and divided amounts.")

    # Combine due dates and amounts into a formatted string
    payment_schedule = "\n".join(
        f"{i + 1}. {due_date} - {amount} {currency}"
        for i, (due_date, amount) in enumerate(zip(due_dates, divided_amounts))
    )

    return {
        "ru": (
            f"☑️Отлично! Теперь давайте отправим реферальную ссылку или выберем другого человека из нашего списка, чтобы он подтвердил этот долг и всё было правильно.\n\n"
            f"📑Информация про долг:\n"
            f"👤 Заёмщик: {creditor_name}\n"
            f"📞 Номер телефона заёмщика: {creditor_phone_number}\n"
            f"👤 Должник: {user['fullname']}\n"
            f"📞 Номер телефона должника: {user['phone_number']}\n"
            f"💰 Сумма: {amount} {currency_parse[currency]['ru']}\n"
            f"📅 Дата выдачи: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 График платежей:\n{payment_schedule}\n"
            f"💬 Комментарий: {comment if comment else 'Без комментария'}\n\n"
            f"📝Нажмите кнопку ниже, чтобы принять или отклонить запрос."
        ),
        "uz": (
            f"☑️Ajoyib! Keling, ushbu qarzni tasdiqlash va hamma narsa rasmiy bo'lishi uchun qarz beruvchiga havolani yuboramiz yoki ro'yxatimizdan u odamni tanlaymiz.\n\n"
            f"📑Qarz haqida ma'lumot:\n"
            f"👤 Qarz beruvchi: {creditor_name}\n"
            f"📞 Telefon raqami: {creditor_phone_number}\n"
            f"👤 Qarz oluvchi: {user['fullname']}\n"
            f"📞 Telefon raqami: {user['phone_number']}\n"
            f"💰 Summa: {amount} {currency_parse[currency]['uz']}\n"
            f"📅 Qarz berilgan sana: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 To'lovlar jadvali:\n{payment_schedule}\n"
            f"💬 Izoh: {comment if comment else 'Izohsiz'}\n\n"
            f"📝So'rovni qabul yoki rad etish uchun pastdagi tugmani bosing."
        ),
        "oz": (
            f"☑️Ажойиб! Келинг, ушбу қарзни тасдиқлаш ва ҳамма нарса расмий бўлиши учун қарз берувчга ҳаволани юборамиз ёки рўйхатимиздан у одамни танлаймиз.\n\n"
            f"📑Қарз ҳақида маълумот:\n"
            f"👤 Қарз берувчи: {creditor_name}\n"
            f"📞 Телефон рақами: {creditor_phone_number}\n"
            f"👤 Қарз олувчи: {user['fullname']}\n"
            f"📞 Телефон рақами: {user['phone_number']}\n"
            f"💰 Сумма: {amount} {currency_parse[currency]['oz']}\n"
            f"📅 Қарз берилган сана: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 Тўловлар жадвали:\n{payment_schedule}\n"
            f"💬 Изоҳ: {comment if comment else 'Изоҳсиз'}\n\n"
            f"📝Сўровни қабул ёки рад этиш учун пастдаги тугмани босинг."
        )
    }

def creation_givedebt_text(user, data, comment=""):
    creditor_name = data.get("givedebt_debtor")
    creditor_phone_number = data.get("givedebt_debtor_phone")
    amount = int(data.get("givedebt_amount"))
    currency = data.get("givedebt_currency")
    loan_date = datetime.strptime(data.get("givedebt_loan_date"), "%d.%m.%Y")

    # Parse due dates and divided amounts
    due_dates = [
        datetime.strptime(item["due_date"], "%d.%m.%Y").strftime("%d.%m.%Y")
        for item in data.get("givedebt_due_date", [])
    ]
    divided_amounts = [
        int(item["divided_amount"])
        for item in data.get("givedebt_amounts", [])
    ]

    # Ensure due_dates and divided_amounts have the same length
    if len(due_dates) != len(divided_amounts):
        raise ValueError("Mismatch between due dates and divided amounts.")

    # Combine due dates and amounts into a formatted string
    payment_schedule = "\n".join(
        f"{i + 1}. {due_date} - {amount} {currency}"
        for i, (due_date, amount) in enumerate(zip(due_dates, divided_amounts))
    )

    return {
        "ru": (
            f"☑️Отлично! Теперь давайте отправим реферальную ссылку или выберем другого человека из нашего списка, чтобы он подтвердил этот долг и всё было официально.\n\n"
            f"📑Информация про долг:\n"
            f"👤 Заёмщик: {user['fullname']}\n"
            f"📞 Номер телефона заёмщика: {user['phone_number']}\n"
            f"👤 Должник: {creditor_name}\n"
            f"📞 Номер телефона должника: {creditor_phone_number}\n"
            f"💰 Сумма: {amount} {currency_parse[currency]['ru']}\n"
            f"📅 Дата выдачи: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 График платежей:\n{payment_schedule}\n"
            f"💬 Комментарий: {comment if comment else 'Без комментария'}\n\n"
            f"📝Нажмите кнопку ниже, чтобы принять или отклонить запрос."
        ),
        "uz": (
            f"☑️Ajoyib! Keling, ushbu qarzni tasdiqlash va hamma narsa rasmiy bo'lishi uchun qarz beruvchiga havolani yuboramiz yoki ro'yxatimizdan u odamni tanlaymiz.\n\n"
            f"📑Qarz haqida ma'lumot:\n"
            f"👤 Qarz beruvchi: {user['fullname']}\n"
            f"📞 Telefon raqami: {user['phone_number']}\n"
            f"👤 Qarz oluvchi: {creditor_name}\n"
            f"📞 Telefon raqami: {creditor_phone_number}\n"
            f"💰 Summa: {amount} {currency_parse[currency]['uz']}\n"
            f"📅 Qarz berilgan sana: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 To'lovlar jadvali:\n{payment_schedule}\n"
            f"💬 Izoh: {comment if comment else 'Izohsiz'}\n\n"
            f"📝So'rovni qabul yoki rad etish uchun pastdagi tugmani bosing."
        ),
        "oz": (
            f"☑️Ажойиб! Келинг, ушбу қарзни тасдиқлаш ва ҳамма нарса расмий бўлиши учун қарз берувчга ҳаволани юборамиз ёки рўйхатимиздан у одамни танлаймиз.\n\n"
            f"📑Қарз ҳақида маълумот:\n"
            f"👤 Қарз берувчи: {user['fullname']}\n"
            f"📞 Телефон рақами: {user['phone_number']}\n"
            f"👤 Қарз олувчи: {creditor_name}\n"
            f"📞 Телефон рақами: {creditor_phone_number}\n"
            f"💰 Сумма: {amount} {currency_parse[currency]['oz']}\n"
            f"📅 Қарз берилган сана: {loan_date.strftime('%d.%m.%Y')}\n"
            f"📅 Тўловлар жадвали:\n{payment_schedule}\n"
            f"💬 Изоҳ: {comment if comment else 'Изоҳсиз'}\n\n"
            f"📝Сўровни қабул ёки рад этиш учун пастдаги тугмани босинг."
        )
    }

accept_text = {
    "ru": "☑️Принять",
    "uz": "☑️Qabul qilish",
    "oz": "☑️Қабул қилиш"
}

reject_text = {
    "ru": "❌Отклонить",
    "uz": "❌Rad etish",
    "oz": "❌Рад этиш"
}

emoji_explanation = {
    "uz": (
        "✅ - Miqdor to'liq to'langan\n"
        "❌ - Miqdor to'liq to'lanmagan"
    ),
    "ru": (
        "✅ - Сумма полностью оплачена\n"
        "❌ - Сумма не оплачена полностью"
    ),
    "oz": (
        "✅ - Миқдор тўлиқ тўланган\n"
        "❌ - Миқдор тўлиқ тўланмаган"
    )
}

import json
from datetime import datetime

async def debt_text(debt):
    # Fetching user information
    debtor = await get_user_by_id(debt['debtor_id'])
    borrower = await get_user_by_id(debt['borrower_id'])

    # Get currency symbol
    currency = currency_parse[debt['currency']]['symbol']

    due_dates = json.loads(debt['due_date'])
    divided_amounts = json.loads(debt['amounts'])
    paid_amounts = json.loads(qarz_debt.get('paid_amount', "{}"))  # Default to empty dict if None

    # Calculate the paid amounts applied to each installment
    remaining_amounts = divided_amounts[:]
    total_paid = sum(paid_amounts.values())
    paid_per_date = {}

    for date, paid in paid_amounts.items():
        paid_per_date[date] = paid

    # Deduct payments from each divided amount
    for i, amount in enumerate(divided_amounts):
        for date, paid in paid_per_date.items():
            if paid <= 0:
                continue
            if amount <= paid:
                remaining_amounts[i] = 0
                paid_per_date[date] -= amount
                break
            else:
                remaining_amounts[i] -= paid
                paid_per_date[date] = 0

    # Build the payment schedule
    payment_schedule = "\n".join(
        f"{i + 1}. {due_date} - {amount} {currency} " +
        (f"✅" if remaining_amounts[i] == 0 else f"❌ (qolgan miqdor: {remaining_amounts[i]} {currency})")
        for i, (due_date, amount) in enumerate(zip(due_dates, divided_amounts))
    )

    # Return the formatted debt info
    return {
        "uz": (
            f"📑 Qarz haqida ma'lumot:\n\n"
            f"👤 Qarz beruvchi: {debtor['fullname']}\n"
            f"📞 Qarz beruvchi telefon raqami: {debtor['phone_number']}\n"
            f"👤 Qarzdor: {borrower['fullname']}\n"
            f"📞 Qarzdor telefon raqami: {borrower['phone_number']}\n"
            f"💰 Qarz miqdori: {debt['full_amount']} {currency}\n"
            f"📅 Qarz berilgan kun: {debt['loan_date'].strftime('%d.%m.%Y')}\n"
            f"📅 Qarz berish jadvali:\n{payment_schedule}\n\n"
            f"{emoji_explanation['uz']}\n\n"
            f"💬 Izoh: {qarz_debt.get('comment') if qarz_debt.get('comment') else 'Izoh qoldirilmagan'}"
        ),
        "ru": (
            f"📑 Информация о долге:\n\n"
            f"👤 Заёмщик: {debtor['fullname']}\n"
            f"📞 Номер заёмщика: {debtor['phone_number']}\n"
            f"👤 Должник: {borrower['fullname']}\n"
            f"📞 Номер должника: {borrower['phone_number']}\n"
            f"💰 Сумма долга: {debt['full_amount']} {currency}\n"
            f"📅 Дата получения долга: {debt['loan_date'].strftime('%d.%m.%Y')}\n"
            f"📅 График платежей:\n{payment_schedule}\n\n"
            f"{emoji_explanation['ru']}\n\n"
            f"💬 Комментарий: {qarz_debt.get('comment') if qarz_debt.get('comment') else 'Комментарий не оставлен'}"
        ),
        "oz": (
            f"📑 Қарз ҳақида маълумот:\n\n"
            f"👤 Қарз берувчи: {debtor['fullname']}\n"
            f"📞 Қарз берувчи телефон рақами: {debtor['phone_number']}\n"
            f"👤 Қарздор: {borrower['fullname']}\n"
            f"📞 Қарздор телефон рақами: {borrower['phone_number']}\n"
            f"💰 Қарз миқдори: {debt['full_amount']} {currency}\n"
            f"📅 Қарз берилган кун: {debt['loan_date'].strftime('%d.%m.%Y')}\n"
            f"📅 Қарз бериш жадвали:\n{payment_schedule}\n\n"
            f"{emoji_explanation['oz']}\n\n"
            f"💬 Изоҳ: {qarz_debt.get('comment') if qarz_debt.get('comment') else 'Изоҳ кўлдирилмаган'}"
        )
    }

amount_entered_successfully = {
    "ru": "✅ Сумма успешно введена.",
    "uz": "✅ Summa muvaffaqiyatli kiritildi.",
    "oz": "✅ Сумма муваффақиятли киритилди."
}

enter_valid_amount = {
    "ru": "❗️Введите корректную сумму.",
    "uz": "❗️To'g'ri summani kiriting.",
    "oz": "❗️Тўғри суммани киритинг."
}

def debt_completed(debt_id) -> str:
    return {
        "ru": f"✅ Долг \"{debt_id}\" успешно завершен.",
        "uz": f"✅ \"{debt_id}\" Qarz muvaffaqiyatli yakunlandi.",
        "oz": f"✅ \"{debt_id}\" Қарз муваффақиятли якунланди."
    }

def user_data(user):
    return {
        "ru": (
            f"👤 Имя: {user['fullname']}\n"
            f"📞 Номер телефона: {user['phone_number']}\n"
            f"🎂 День рождения: {user['birthdate']}\n"
            f"⚙️ Язык: {user['lang']}\n\n"
            f"📝 Нажмите кнопку ниже, чтобы изменить данные."
        ),
        "uz": (
            f"👤 Ism: {user['fullname']}\n"
            f"📞 Telefon raqami: {user['phone_number']}\n"
            f"🎂 Tug'ilgan kun: {user['birthdate']}\n"
            f"⚙️ Til: {user['lang']}\n\n"
            f"📝 Ma'lumotlarni o'zgartirish uchun pastdagi tugmani bosing."
        ),
        "oz": (
            f"👤 Исм: {user['fullname']}\n"
            f"📞 Телефон рақами: {user['phone_number']}\n"
            f"🎂 Туғилган кун: {user['birthdate']}\n"
            f"⚙️ Тил: {user['lang']}\n\n"
            f"📝 Маълумотларни ўзгартириш учун пастдаги тугмани босинг."
        )
    }