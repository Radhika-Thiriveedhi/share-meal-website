from utils.security import hash_password, verify_password, sanitize_input
from utils.validators import validate_email, validate_password_strength, validate_donation_input
from datetime import datetime, timedelta

def test_password_hashing():
    pwd = "StrongPassword@123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(hashed, pwd) is True
    assert verify_password(hashed, "WrongPassword") is False

def test_password_strength_validation():
    valid, msg = validate_password_strength("Short1A")
    assert not valid
    assert "8 characters" in msg

    valid, msg = validate_password_strength("alllowercase123")
    assert not valid
    assert "uppercase" in msg

    valid, msg = validate_password_strength("ALLUPPERCASE123")
    assert not valid
    assert "lowercase" in msg

    valid, msg = validate_password_strength("NoDigitsHere!")
    assert not valid
    assert "number" in msg

    valid, _ = validate_password_strength("ValidPass123")
    assert valid is True

def test_email_validation():
    assert validate_email("donor@example.com") is True
    assert validate_email("invalid-email") is False
    assert validate_email("") is False

def test_sanitize_input():
    unsafe = "<script>alert('xss')</script>"
    safe = sanitize_input(unsafe)
    assert "<script>" not in safe
    assert "&lt;script&gt;" in safe
