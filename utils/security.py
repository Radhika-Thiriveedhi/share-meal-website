import secrets
import html
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

def hash_password(password: str) -> str:
    """Securely hash a user password using pbkdf2:sha256."""
    return generate_password_hash(password, method="pbkdf2:sha256")

def verify_password(password_hash: str, password: str) -> bool:
    """Verify password against stored secure hash."""
    if not password_hash or not password:
        return False
    return check_password_hash(password_hash, password)

def generate_csrf_token() -> str:
    """Generate or retrieve unique CSRF token for the current session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf_token(token: str) -> bool:
    """Validate submitted token against session CSRF token."""
    session_token = session.get('_csrf_token')
    if not session_token or not token:
        return False
    return secrets.compare_digest(session_token, token)

def sanitize_input(value: str) -> str:
    """Sanitize user string input to prevent XSS."""
    if not isinstance(value, str):
        return value
    return html.escape(value.strip())
