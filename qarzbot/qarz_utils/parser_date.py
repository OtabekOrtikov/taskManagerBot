from datetime import datetime, timedelta

from qarz_utils.basic_texts import invalid_date

def parse_date(date_text: str, lang: str, reference_date: datetime = None) -> str:
    today = datetime.now()
    max_year = 2026
    min_date = datetime(today.year - 5, 1, 1)  # Allow dates up to 5 years before today
    reference_date = reference_date or today

    if date_text == "today" or date_text in [
        today.strftime("%d.%m"),
        today.strftime("%d.%m.%y"),
        today.strftime("%d.%m.%Y")
    ]:
        return today.strftime("%d.%m.%Y")
    
    formats = ["%d.%m", "%d.%m.%y", "%d.%m.%Y"]

    # Try parsing the date with each format
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_text, fmt)
            
            # Handle the case where only day and month are provided
            if fmt == "%d.%m":
                parsed_date = parsed_date.replace(year=reference_date.year)
                # Roll over to the next year if parsed date is before the reference date
                if parsed_date < reference_date:
                    parsed_date = parsed_date.replace(year=reference_date.year + 1)

            elif fmt == "%d.%m.%y" and parsed_date.year < 2000:
                # Ensure two-digit years are interpreted in the 2000s
                parsed_date = parsed_date.replace(year=parsed_date.year + 2000)

            # Ensure the date is within the valid range
            if min_date <= parsed_date <= datetime(max_year, 12, 31):
                return parsed_date.strftime("%d.%m.%Y")
        except ValueError:
            continue

    # Raise an error if parsing fails
    raise ValueError(invalid_date[lang])
