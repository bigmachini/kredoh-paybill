import phonenumbers
from phonenumbers import carrier

from app.utils import get_carrier_info, format_phone_number, get_signature


def test_get_carrier_info():
    phone_number = "+254712345678"
    expected_carrier = "SAFARICOM"

    def mock_parse(phone_number, region):
        return True

    def mock_name_for_number(ke_number, language):
        return "Safaricom"

    phonenumbers.parse = mock_parse
    phonenumbers.carrier.name_for_number = mock_name_for_number

    result = get_carrier_info(phone_number)

    assert result == expected_carrier


def test_format_phone_number():
    phone_number = "254712345678"
    expected_formatted_number = "0712345678"

    result = format_phone_number(phone_number)

    assert result == expected_formatted_number


def test_get_signature():
    message = "Hello, World!"
    api_key = "my_api_key"
    expected_signature = "2d73f1932af5c382136e06f4f550c9990b42e2b028b68e36211fe94a13dd0f10"

    result = get_signature(message, api_key)

    assert result == expected_signature
