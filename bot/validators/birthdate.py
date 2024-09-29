from datetime import datetime

def validate_birthdate(_date: str) -> bool:
    """
    Validates that the string is a date in format '%d-%m-%Y'
    """
    try:
        # Try to parse the date string with the given format
        datetime.strptime(_date, '%d-%m-%Y')
        return True
    except ValueError:
        # If parsing fails, it's not a valid date in the expected format
        return False
