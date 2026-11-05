from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from utils.security import validate_csrf_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in to access this page.", "warning")
                return redirect(url_for('auth.login', next=request.path))
            user_role = session.get('role')
            if user_role not in allowed_roles and user_role != 'admin':
                flash("You do not have permission to view that section.", "danger")
                return redirect(url_for('public.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        status = session.get('verification_status')
        role = session.get('role')
        if role != 'admin' and status != 'verified':
            return redirect(url_for('auth.pending_verification'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            if not token or not validate_csrf_token(token):
                abort(400, description="Invalid or missing CSRF security token.")
        return f(*args, **kwargs)
    return decorated_function
