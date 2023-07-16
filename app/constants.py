# KYANDA CONSTANTS
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
AIRTIME_RESPONSE_FAILED = "airtime-response-failed"
AIRTIME_RESPONSE_SUCCESS = "airtime-response-success"

SMS_RESPONSE_FAILED = "sms-response-failed"
SMS_RESPONSE_SUCCESS = "sms-response-success"

ALLOWED_TELCOS = ["AIRTEL", "SAFARICOM", "TELKOM", "EQUITEL", "FAIBA"]
DUPLICATE_TRANSACTION_ERROR = "Duplicate transaction"

C2B_PAYBILL = "c2b-paybill"
REVERSAL_RESPONSE_FAILED = "reversal-response-failed"
REVERSAL_RESPONSE_SUCCESS = "reversal-response-success"
REVERSAL_CALLBACK = "reversal-callback"
REVERSALS = "reversals"
