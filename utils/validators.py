import re
from datetime import datetime
from utils.date_helpers import parse_iso

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^[\d\+\-\s\(\)]{7,20}$")

def validate_email(email: str) -> bool:
    if not email or len(email) > 120:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_password_strength(password: str):
    """
    Validate password has at least 8 chars, 1 uppercase, 1 lowercase, 1 number.
    Returns (is_valid: bool, error_message: str).
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, ""

def validate_phone(phone: str) -> bool:
    if not phone:
        return False
    return bool(PHONE_REGEX.match(phone.strip()))

def validate_donation_input(data: dict):
    """
    Strict server-side validation for food donation submissions.
    Returns (is_valid: bool, errors: dict).
    """
    errors = {}
    if not data.get("food_name", "").strip():
        errors["food_name"] = "Food item name is required."
    if not data.get("food_category"):
        errors["food_category"] = "Please select a valid food category."
    try:
        qty = float(data.get("quantity_published", 0))
        if qty <= 0:
            errors["quantity_published"] = "Quantity must be greater than zero."
    except (ValueError, TypeError):
        errors["quantity_published"] = "Quantity must be a valid number."
        
    if not data.get("unit", "").strip():
        errors["unit"] = "Unit of measurement is required."
        
    # Food safety timelines
    prep_dt = parse_iso(data.get("preparation_datetime"))
    if not prep_dt:
        errors["preparation_datetime"] = "Valid preparation date and time is required."
    elif prep_dt > datetime.utcnow():
        errors["preparation_datetime"] = "Preparation time cannot be in the future."
        
    deadline = parse_iso(data.get("collection_deadline"))
    if not deadline:
        errors["collection_deadline"] = "Collection deadline is required."
    elif deadline <= datetime.utcnow():
        errors["collection_deadline"] = "Collection deadline must be in the future."
    elif prep_dt and deadline <= prep_dt:
        errors["collection_deadline"] = "Collection deadline must be after preparation time."
        
    if not data.get("storage_conditions"):
        errors["storage_conditions"] = "Storage conditions must be specified for food safety."
    if not data.get("packaging_condition"):
        errors["packaging_condition"] = "Packaging integrity condition is required."
    if not data.get("pickup_address", "").strip():
        errors["pickup_address"] = "Pickup location address is required."
        
    return len(errors) == 0, errors
