import re


def validate_phone(phone: str) -> bool:
    """
    Validates that the string is a valid phone number. A valid phone number can:
    - Start with an optional '+' for international numbers
    - Contain digits, spaces, hyphens, and parentheses
    - Be at least 7 digits long
    """
    phone_pattern = r'^\+?[\d\s\-()]{7,}$'

    if re.match(phone_pattern, phone):
        return True
    return False
