import re


def validate_email(email: str) -> bool:
    """Checks if the string is email with help of regular expression"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(pattern, email):
        return True
    return False
