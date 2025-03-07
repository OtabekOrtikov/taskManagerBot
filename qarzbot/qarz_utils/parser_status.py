def parse_status(status):
    if status == 'active':
        return {
            "ru": {
                "full": "🟡 Не закрытый долг",
                "short": "🟡"
            },
            "oz": {
                "full": "🟡 Тўланмаган қарз",
                "short": "🟡"
            },
            "uz": {
                "full": "🟡 To'lanmagan qarz",
                "short": "🟡"
            }
        }
    elif status == 'closed' or status == "completed":
        return {
            "ru": {
                "full": "🟢 Закрытый долг",
                "short": "🟢"
            },
            "oz": {
                "full": "🟢 Тўланган қарз",
                "short": "🟢"
            },
            "uz": {
                "full": "🟢 To'langan qarz",
                "short": "🟢"
            }
        }
    elif status == 'overdue':
        return {
            "ru": {
                "full": "🔴 Просроченный долг",
                "short": "🔴"
            },
            "oz": {
                "full": "🔴 Муддати ўтган қарз",
                "short": "🔴"
            },
            "uz": {
                "full": "🔴 Muddati o'tgan qarz",
                "short": "🔴"
            }
        }
    else:
        return {
            "ru": {
                "full": "🟠 Черновик",
                "short": "🟠"
            },
            "oz": {
                "full": "🟠 Қоралама",
                "short": "🟠"
            },
            "uz": {
                "full": "🟠 Qoralama",
                "short": "🟠"
            }
        }