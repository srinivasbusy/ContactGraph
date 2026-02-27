import phonenumbers
from phonenumbers import NumberParseException


def normalize_phone(phone: str, default_region: str = "US") -> str:
    """Normalize a phone number to E.164 format."""
    try:
        parsed = phonenumbers.parse(phone, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        pass
    # Return stripped version as fallback so callers can decide
    return phone.strip()


def is_valid_phone(phone: str, default_region: str = "US") -> bool:
    """Return True if the phone number is valid."""
    try:
        parsed = phonenumbers.parse(phone, default_region)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False
