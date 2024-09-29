import re


def validate_name(name: str) -> bool:
    """
    Validates that the string is a name. A valid name should:
    - Only contain letters (both uppercase and lowercase), spaces, or hyphens
    - Start and end with a letter
    - Not contain numbers or special characters
    """
    pattern = r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$"

    if re.match(pattern, name):
        return True
    return False
