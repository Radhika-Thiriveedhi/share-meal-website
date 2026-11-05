from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config
from utils.decorators import login_required, csrf_protected

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication with role redirect and 1-click test shortcuts."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        success, message, user = AuthService.authenticate(email, password)
        if success:
            flash(message, "success")
            # Redirect to role-specific dashboard
            role = user.get('role')
            if role == 'donor':
                return redirect(url_for('donor.dashboard'))
            elif role == 'organization':
                return redirect(url_for('org.dashboard'))
            elif role == 'volunteer':
                return redirect(url_for('volunteer.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('public.index'))
        else:
            flash(message, "danger")
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Clear session and log out."""
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('public.index'))

@auth_bp.route('/register')
def register():
    """Role selection portal for registration."""
    return render_template('auth/register.html')

@auth_bp.route('/register/<role>', methods=['GET', 'POST'])
def register_role(role):
    """Specific role registration form (donor, organization, volunteer)."""
    if role not in ['donor', 'organization', 'volunteer']:
        flash("Invalid registration role.", "danger")
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        postal_code = request.form.get('postal_code', '')
        
        # Role specific fields
        org_type = request.form.get('org_type', '')
        org_name = request.form.get('org_name', '')
        license_number = request.form.get('license_number', '')
        tax_id = request.form.get('tax_id', '')
        operating_hours = request.form.get('operating_hours', '')

        success, message, user = AuthService.register_user(
            email=email,
            password=password,
            name=name,
            role=role,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            org_type=org_type,
            org_name=org_name,
            license_number=license_number,
            tax_id=tax_id,
            operating_hours=operating_hours
        )

        if success:
            flash(message, "success")
            # Automatically sign in into pending state
            AuthService.authenticate(email, password)
            return redirect(url_for('auth.pending_verification'))
        else:
            flash(message, "danger")

    template_map = {
        'donor': 'auth/register_donor.html',
        'organization': 'auth/register_org.html',
        'volunteer': 'auth/register_volunteer.html'
    }
    return render_template(template_map[role], role=role)

@auth_bp.route('/pending-verification')
def pending_verification():
    """Screen for users awaiting administrative verification."""
    user = storage.find_by_id(Config.USERS_FILE, session.get('user_id'))
    if user and user.get('verification_status') == 'verified':
        session['verification_status'] = 'verified'
        role = user.get('role')
        if role == 'donor':
            return redirect(url_for('donor.dashboard'))
        elif role == 'organization':
            return redirect(url_for('org.dashboard'))
        elif role == 'volunteer':
            return redirect(url_for('volunteer.dashboard'))
        return redirect(url_for('public.index'))
        
    return render_template('auth/pending_verification.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management and password change."""
    user = storage.find_by_id(Config.USERS_FILE, session.get('user_id'))
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.logout'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            updates = {
                'name': request.form.get('name', ''),
                'phone': request.form.get('phone', ''),
                'address': request.form.get('address', ''),
                'city': request.form.get('city', ''),
                'postal_code': request.form.get('postal_code', ''),
                'operating_hours': request.form.get('operating_hours', '')
            }
            if user.get('role') in ['donor', 'organization']:
                updates['org_name'] = request.form.get('org_name', '')
                
            AuthService.update_profile(user['id'], updates)
            flash("Profile details updated successfully.", "success")
            return redirect(url_for('auth.profile'))

        elif action == 'change_password':
            curr = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')

            if new_pwd != confirm_pwd:
                flash("New passwords do not match.", "warning")
            else:
                success, msg = AuthService.change_password(user['id'], curr, new_pwd)
                flash(msg, "success" if success else "danger")
            return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=user)
