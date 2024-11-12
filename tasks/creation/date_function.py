from datetime import datetime

def parse_and_validate_date(date_text: str, reference_date: datetime = None) -> str:
    """Parses the date from text and ensures it follows 'dd.mm.yyyy' format, interpreting today's date."""
    today = datetime.now()
    max_year = 2026
    reference_date = reference_date or today

    # Special case for "today" keyword
    if date_text.lower() == "today" or date_text == today.strftime("%d.%m") or date_text == today.strftime("%d.%m.%y") or date_text == today.strftime("%d.%m.%Y"):
        return today.strftime("%d.%m.%Y")

    # Define allowed date formats
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
            if reference_date <= parsed_date <= datetime(max_year, 12, 31):
                return parsed_date.strftime("%d.%m.%Y")
        except ValueError:
            continue

    # Raise an error if parsing fails
    raise ValueError("Invalid date format or date out of range. Please enter a date in 'dd.mm', 'dd.mm.yy', or 'dd.mm.yyyy' format.")
