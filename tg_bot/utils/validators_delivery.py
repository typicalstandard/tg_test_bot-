import re

def validate_address(address: str) -> bool:
    return len(address) >= 5

def validate_phone(phone: str) -> bool:
    phone_pattern = r"^\+?\d{10,15}$"
    return bool(re.match(phone_pattern, phone))

def validate_email(email: str) -> bool:
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))
