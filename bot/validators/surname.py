import re


def validate_surname(surname: str) -> bool:
    """
    Validates that the string is a surname. A valid surname should:
    - Only contain letters (uppercase or lowercase), spaces, hyphens, or apostrophes
    - Start and end with a letter
    - Not contain numbers or special characters (except spaces, hyphens, or apostrophes)
    """
    surname_pattern = r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$"

    if re.match(surname_pattern, surname):
        return True
    return False
