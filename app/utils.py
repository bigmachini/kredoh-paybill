from typing import Tuple

import phonenumbers
from phonenumbers import carrier


def get_carrier_info(phone_number: str) -> [Tuple[str, str], None]:
    try:
        ke_number = phonenumbers.parse(phone_number, "KE")
        if ke_number:
            _carrier = carrier.name_for_number(ke_number, "en")
            if _carrier == 'JTL':
                _carrier = 'FAIBA'
            print(f"get_carrier_info:: _carrier: {_carrier}")
            print("ke_number.national_number", f"0{ke_number.national_number}")
            return _carrier.upper(), f"0{ke_number.national_number}"
        else:
            return None
    except phonenumbers.phonenumberutil.NumberParseException as ex:
        print("ex", ex)


def format_phone_number(phone_number):
    return f'0{phone_number[3:]}'


def get_signature(message: str, api_key: str) -> str:
    import hashlib
    import hmac
    message = bytes(message, 'utf-8')
    secret = bytes(api_key, 'utf-8')
    signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
    return signature
# write a test for get_signature
