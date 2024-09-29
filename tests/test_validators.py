import pytest

from bot.validators.birthdate import validate_birthdate
from bot.validators.email import validate_email
from bot.validators.name import validate_name
from bot.validators.phone import validate_phone
from bot.validators.surname import validate_surname


def test_validate_name_valid():
    assert validate_name("John")
    assert validate_name("Anne-Marie")
    assert validate_name("O'Neil")


def test_validate_name_invalid():
    """
    1) Test for name with digit
    2) Test for name with special character
    3) Test for name from empty string
    """
    assert not validate_name("John123")
    assert not validate_name("John@Doe")
    assert not validate_name("")


def test_validate_surname_valid():
    assert validate_surname("O'Connor")
    assert validate_surname("Smith-Jones")
    assert validate_surname("McCarthy")


def test_validate_surname_invalid():
    """
    1) Test for surname with digits
    2) Test for surname with special characters
    3) Test for surname made from empty string

    """
    assert not validate_surname("Smith123")  # Contains digits
    assert not validate_surname("Smith@Jones")  # Contains special character
    assert not validate_surname("")  # Empty string


def test_validate_email_valid():
    assert validate_email("test@example.com")
    assert validate_email("user.name+tag+sorting@example.co.uk")
    assert validate_email("test_email123@test-domain.com")


def test_validate_email_invalid():
    """
    1) Test for email from plaintext
    2) Test for email without @ sign
    3) Test for email with invalid domain
    """
    assert not validate_email("plainaddress")
    assert not validate_email("missingatsign.com")
    assert not validate_email("invalid@domain@domain.com")


def test_validate_phone_valid():
    assert validate_phone("+1 (555) 123-4567")
    assert validate_phone("555-1234")
    assert validate_phone("123 456 7890")

def test_validate_phone_invalid():
    """
    1) Test for phone with too short phone length
    2) Test for phone with invalid characters
    3) Test for phone with too many + symbols
    """
    assert not validate_phone("12345")
    assert not validate_phone("123-456-78X0")
    assert not validate_phone("++1234567890")


def test_validate_birthdate_valid():
    assert validate_birthdate("29-09-1990")
    assert validate_birthdate("01-01-2000")
    assert validate_birthdate("15-07-1985")


def test_validate_birthdate_invalid():
    """
    1) Test for birthdate with incorrect format
    2) Test for invalid date
    3) Test for date with incorrect delimiter
    """
    assert not validate_birthdate("1990-09-29")  # Incorrect format
    assert not validate_birthdate("31-02-2000")  # Invalid date
    assert not validate_birthdate("15/07/1985")  # Incorrect delimiter