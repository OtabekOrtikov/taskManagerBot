from datetime import datetime

def parse_date(date_text: str) -> str:
    """Parses the date from text and adds the year if missing."""
    today = datetime.now()
    max_year = 2026

    # Attempt to parse the date with different formats
    for fmt in ("%d.%m", "%d.%m.%y", "%d.%m.%Y"):
        try:
            parsed_date = datetime.strptime(date_text, fmt)
            # If no year was specified, add the current or next year
            if fmt == "%d.%m":
                parsed_date = parsed_date.replace(year=today.year)
                # Only update to next year if parsed_date is strictly before today
                if parsed_date < today and parsed_date.date() != today.date():
                    parsed_date = parsed_date.replace(year=today.year + 1)
            # Ensure the date is within the allowed range
            if today <= parsed_date <= datetime(max_year, 12, 31):
                return parsed_date.strftime("%d.%m.%Y")
        except ValueError:
            continue

    # If parsing fails, raise an error
    raise ValueError("Invalid date format")
