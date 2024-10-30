import re
from datetime import datetime

def validate_date(date_text: str) -> bool:
    # Define regex patterns for the allowed date formats
    patterns = [
        r"^\d{2}\.\d{2}$",            # dd.mm
        r"^\d{2}\.\d{2}\.\d{2}$",      # dd.mm.yy
        r"^\d{2}\.\d{2}\.\d{4}$"       # dd.mm.yyyy
    ]

    # Current date and max date for validation
    today = datetime.now()
    max_date = datetime(2026, 1, 1)

    # Check if the date matches any of the patterns
    if any(re.match(pattern, date_text) for pattern in patterns):
        # Attempt to parse the date to ensure it's valid and within range
        for fmt in ("%d.%m", "%d.%m.%y", "%d.%m.%Y"):
            try:
                parsed_date = datetime.strptime(date_text, fmt)

                # Adjust year if it's a two-digit format and likely refers to this century
                if fmt == "%d.%m" or fmt == "%d.%m.%y":
                    parsed_date = parsed_date.replace(year=today.year)

                # Ensure date is not in the past and does not exceed the max allowed date
                if today.date() <= parsed_date.date() <= max_date.date():
                    return True
            except ValueError:
                continue
    return False