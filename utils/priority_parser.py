async def parse_priority(priority_id: int, lang: str) -> str:
    if priority_id == '1':
        if lang == 'en':
            priority = "Low"
        elif lang == 'ru':
            priority = "Низкий"
        elif lang == 'uz':
            priority = "Past"
    elif priority_id == '2':
        if lang == 'en':
            priority = "Medium"
        elif lang == 'ru':
            priority = "Средний"
        elif lang == 'uz':
            priority = "O'rta"
    else:
        if lang == 'en':
            priority = "High"
        elif lang == 'ru':
            priority = "Высокий"
        elif lang == 'uz':
            priority = "Yuqori"

    return priority