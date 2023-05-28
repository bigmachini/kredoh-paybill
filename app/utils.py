import phonenumbers
from phonenumbers import carrier

KYANDA_ERROR_CODES = {
    "0000": "Request processed sucessfully.",
    "1100": "Transaction created and pending processing.",
    "1101": "Invalid Merchant ID.",
    "1102": "Authentication failed.",
    "1103": "Forbidden access",
    "1104": "Signature Mismatch.",
    "1105": "Payment services unavailable.",
    "1106": "Airtime Service unavailable.",
    "1107": "Insufficient float balance.",
    "1108": "Missing parameter.",
    "1109": "Parameter validation error.",
    "1201": "Invalid Bank Code",
    "5000": "Unexpected error has occurred.",
    "6001": "Cannot register the URL",
    "6002": "Invalid URL format.",
    "7001": "Iransaction not found.",
    "8001": "Invalid account number format.",
    "8002": "Invalid phone number format.",
    "8003": "Invalid Telco.",
    "8004": "Invalid amount format.",
    "8005": "Amount limit exceeded.",
    "8006": "Duplicate transmission.",
    "9001": "Invalid phone number format.",
    "9002": "Invalid transaction channel.",
    "9003": "Invalid amount format.",
    "9004": "Amount limit exceeded.",
    "9005": "Duplicate transmission"
}


def get_carrier_info(phone_number: str) -> str:
    try:
        parsed_number = phonenumbers.parse(phone_number)
        if phonenumbers.is_valid_number(parsed_number):
            carrier_info = carrier.name_for_number(parsed_number, "en")
            return carrier_info
        else:
            return "Invalid phone number"
    except phonenumbers.phonenumberutil.NumberParseException:
        return "Invalid phone number format"
