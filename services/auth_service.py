from flask import session
from storage.json_storage import storage
from storage.models import UserModel
from utils.security import hash_password, verify_password
from utils.validators import validate_email, validate_password_strength
from services.audit_service import AuditService
from services.notification_service import NotificationService
from config import Config

class AuthService:
    @staticmethod
    def register_user(email, password, name, role, phone="", address="", city="", postal_code="",
                      org_type="", org_name="", license_number="", tax_id="", operating_hours=""):
        """Register a new user with server-side validation and audit logging."""
        # 1. Validation
        if not validate_email(email):
            return False, "Invalid email address format.", None
            
        valid_pwd, pwd_err = validate_password_strength(password)
        if not valid_pwd:
            return False, pwd_err, None
            
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters.", None
            
        if role not in Config.ROLES:
            return False, "Invalid role selected.", None

        # 2. Check for duplicate email
        normalized_email = email.strip().lower()
        existing = storage.find_where(Config.USERS_FILE, lambda u: u.get("email") == normalized_email)
        if existing:
            return False, "An account with this email address already exists.", None

        # 3. Create user record
        # Note: All non-admin registrations start as 'pending' verification
        verification_status = "pending"
        pwd_hash = hash_password(password)
        
        user_record = UserModel.create(
            email=normalized_email,
            password_hash=pwd_hash,
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
            operating_hours=operating_hours,
            verification_status=verification_status,
            is_active=True
        )
        
        storage.insert(Config.USERS_FILE, user_record)
        
        # 4. Audit & notification
        AuditService.log_event(
            action="USER_REGISTERED",
            resource_type="user",
            resource_id=user_record["id"],
            details=f"Registered as {role} ({org_name or name})",
            user_id=user_record["id"],
            user_email=user_record["email"],
            user_role=user_record["role"]
        )
        
        NotificationService.notify_admins(
            title="New Account Awaiting Verification",
            message=f"{user_record['name']} registered as a {Config.ROLES.get(role)}. Verification review required.",
            notif_type="info",
            link="/admin/verifications"
        )
        
        return True, "Registration successful. Your account is submitted for verification.", user_record

    @staticmethod
    def authenticate(email, password):
        """Authenticate user credentials and initiate session."""
        normalized_email = email.strip().lower()
        users = storage.find_where(Config.USERS_FILE, lambda u: u.get("email") == normalized_email)
        if not users:
            return False, "Invalid email or password.", None

        user = users[0]
        if not user.get("is_active", True):
            return False, "This account has been suspended. Please contact platform administrators.", None

        if not verify_password(user.get("password_hash"), password):
            AuditService.log_event(
                action="LOGIN_FAILED",
                resource_type="user",
                resource_id=user["id"],
                details=f"Failed login attempt for {normalized_email}",
                user_email=normalized_email
            )
            return False, "Invalid email or password.", None

        # Establish Flask Session
        session.clear()
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['name'] = user['name']
        session['role'] = user['role']
        session['org_name'] = user.get('org_name', '')
        session['verification_status'] = user.get('verification_status', 'pending')
        session.permanent = True

        AuditService.log_event(
            action="LOGIN_SUCCESS",
            resource_type="user",
            resource_id=user["id"],
            details=f"User signed in successfully with role {user['role']}"
        )
        return True, "Welcome back!", user

    @staticmethod
    def update_profile(user_id, updates):
        """Update user profile information."""
        allowed_fields = ['name', 'phone', 'address', 'city', 'postal_code', 'org_name', 'operating_hours']
        filtered_updates = {k: updates[k] for k in allowed_fields if k in updates}
        
        updated = storage.update(Config.USERS_FILE, user_id, filtered_updates)
        if updated:
            session['name'] = updated.get('name', session.get('name'))
            session['org_name'] = updated.get('org_name', session.get('org_name'))
            AuditService.log_event(
                action="PROFILE_UPDATED",
                resource_type="user",
                resource_id=user_id,
                details="Updated profile details"
            )
        return updated

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Verify current password and update to new password."""
        user = storage.find_by_id(Config.USERS_FILE, user_id)
        if not user or not verify_password(user.get("password_hash"), current_password):
            return False, "Current password is incorrect."

        valid, err_msg = validate_password_strength(new_password)
        if not valid:
            return False, err_msg

        storage.update(Config.USERS_FILE, user_id, {"password_hash": hash_password(new_password)})
        AuditService.log_event(
            action="PASSWORD_CHANGED",
            resource_type="user",
            resource_id=user_id,
            details="Password successfully changed"
        )
        return True, "Password changed successfully."
