async def parse_priority(priority_id: int, lang: str) -> str:
    priority = ""
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

async def parse_priority_id(priority: str) -> int:
    priority = priority.lower()
    if priority == "low" or priority == "низкий" or priority == "past":
        priority_id = 1
    elif priority == "medium" or priority == "средний" or priority == "o'rta":
        priority_id = 2
    else:
        priority_id = 3

    return priority_id