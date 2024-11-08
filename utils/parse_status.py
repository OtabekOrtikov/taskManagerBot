async def parse_status(status: str, lang: str) -> str:
    if status == "In progress":
        text = {
            'en': "In progress",
            'ru': "В процессе",
            'uz': "Jarayonda"
        }
    elif status == "Not started":
        text = {
            'en': "Not started",
            'ru': "Не начата",
            'uz': "Boshlanmagan"
        }
    elif status == "Paused":
        text = {
            'en': "Paused",
            'ru': "Приостановлена",
            'uz': "To‘xtatilgan"
        }
    elif status == "Cancelled":
        text = {
            'en': "Cancelled",
            'ru': "Отменена",
            'uz': "Bekor qilingan"
        }
    else:
        text = {
            'en': "Finished",
            'ru': "Завершена",
            'uz': "Yakunlangan"
        }
    
    return text[lang]