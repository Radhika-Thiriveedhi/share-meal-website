from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from storage.json_storage import storage
from services.safety_service import SafetyService
from services.backup_service import BackupService
from services.audit_service import AuditService
from services.notification_service import NotificationService
from services.donation_service import DonationService
from config import Config
from utils.decorators import login_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin control center with platform KPIs, pending verification queue, and safety alerts."""
    users = storage.find_all(Config.USERS_FILE)
    donations = storage.find_all(Config.DONATIONS_FILE)
    requests = storage.find_all(Config.REQUESTS_FILE)
    reports = storage.find_all(Config.SAFETY_REPORTS_FILE)

    pending_verifications = [u for u in users if u.get('verification_status') == 'pending']
    active_reports = [r for r in reports if r.get('status') == 'under_review']
    active_dispatches = [r for r in requests if r.get('status') in ['approved', 'volunteer_assigned', 'picked_up']]

    total_published = sum(float(d.get('quantity_published', 0)) for d in donations)
    total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in donations)

    return render_template(
        'admin/dashboard.html',
        active_page='dashboard',
        pending_verifications_count=len(pending_verifications),
        active_reports_count=len(active_reports),
        active_dispatches_count=len(active_dispatches),
        total_users_count=len(users),
        total_published=total_published,
        total_distributed=total_distributed,
        pending_users=pending_verifications[:5],
        recent_reports=active_reports[:5]
    )

@admin_bp.route('/verifications')
@login_required
@role_required('admin')
def verifications():
    """Manage pending user account verifications."""
    users = storage.find_all(Config.USERS_FILE)
    pending_users = [u for u in users if u.get('verification_status') == 'pending']
    verified_users = [u for u in users if u.get('verification_status') == 'verified']
    return render_template(
        'admin/verifications.html',
        active_page='verifications',
        pending_users=pending_users,
        verified_users=verified_users[:10]
    )

@admin_bp.route('/verifications/<user_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_verification(user_id):
    """Approve a user account verification."""
    user = storage.find_by_id(Config.USERS_FILE, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.verifications'))

    now = datetime.utcnow().isoformat()
    storage.update(Config.USERS_FILE, user_id, {
        'verification_status': 'verified',
        'verified_at': now,
        'verified_by': session.get('name', 'Admin')
    })

    NotificationService.send_notification(
        user_id=user_id,
        title="Account Verified by Administrator!",
        message="Your account credentials have been verified. You now have full access to create or request food donations.",
        notif_type="success",
        link="/auth/profile"
    )

    AuditService.log_event(
        action="VERIFY_USER_APPROVED",
        resource_type="user",
        resource_id=user_id,
        details=f"Approved verification for {user.get('name')} ({user.get('role')})"
    )

    flash(f"Account for {user.get('name')} verified successfully.", "success")
    return redirect(url_for('admin.verifications'))

@admin_bp.route('/verifications/<user_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_verification(user_id):
    """Reject user account verification."""
    reason = request.form.get('reason', 'Verification credentials could not be validated.')
    user = storage.find_by_id(Config.USERS_FILE, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.verifications'))

    storage.update(Config.USERS_FILE, user_id, {
        'verification_status': 'rejected',
        'verification_notes': reason
    })

    NotificationService.send_notification(
        user_id=user_id,
        title="Account Verification Not Approved",
        message=f"Your registration could not be verified: {reason}. Please update your profile with valid documentation.",
        notif_type="danger",
        link="/auth/profile"
    )

    AuditService.log_event(
        action="VERIFY_USER_REJECTED",
        resource_type="user",
        resource_id=user_id,
        details=f"Rejected verification for {user.get('name')}: {reason}"
    )

    flash(f"Verification rejected for {user.get('name')}.", "info")
    return redirect(url_for('admin.verifications'))

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    """User directory with role filtering and account activation toggle."""
    role_filter = request.args.get('role', 'all')
    all_users = storage.find_all(Config.USERS_FILE)
    if role_filter != 'all':
        all_users = [u for u in all_users if u.get('role') == role_filter]
        
    return render_template('admin/users.html', active_page='users', users=all_users, role_filter=role_filter)

@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    """Suspend or reactivate user account."""
    user = storage.find_by_id(Config.USERS_FILE, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.users'))

    new_active = not user.get('is_active', True)
    storage.update(Config.USERS_FILE, user_id, {'is_active': new_active})
    status_str = "reactivated" if new_active else "suspended"

    AuditService.log_event(
        action="TOGGLE_USER_STATUS",
        resource_type="user",
        resource_id=user_id,
        details=f"Account {status_str} for {user.get('email')}"
    )

    flash(f"User account for {user.get('name')} {status_str}.", "info")
    return redirect(url_for('admin.users'))

@admin_bp.route('/donations')
@login_required
@role_required('admin')
def donations():
    """Platform-wide donations oversight."""
    DonationService.sweep_expired_donations()
    all_donations = storage.find_all(Config.DONATIONS_FILE)
    all_donations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('admin/donations.html', active_page='donations', donations=all_donations)

@admin_bp.route('/requests')
@login_required
@role_required('admin')
def requests():
    """Platform-wide requests oversight."""
    all_requests = storage.find_all(Config.REQUESTS_FILE)
    all_requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('admin/requests.html', active_page='requests', requests=all_requests)

@admin_bp.route('/safety-reports')
@login_required
@role_required('admin')
def safety_reports():
    """Food safety triage board."""
    reports = SafetyService.get_all_reports()
    return render_template('admin/safety_reports.html', active_page='safety', reports=reports)

@admin_bp.route('/safety-reports/<report_id>')
@login_required
@role_required('admin')
def safety_detail(report_id):
    """Detailed safety report investigation."""
    report = SafetyService.get_report_by_id(report_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('admin.safety_reports'))

    donation = DonationService.get_donation_by_id(report.get('donation_id'))
    return render_template('admin/safety_detail.html', active_page='safety', report=report, donation=donation)

@admin_bp.route('/safety-reports/<report_id>/resolve', methods=['POST'])
@login_required
@role_required('admin')
def resolve_safety_report(report_id):
    """Execute administrative determination for a safety incident."""
    admin_id = session.get('user_id')
    resolution = request.form.get('resolution')
    notes = request.form.get('admin_notes', '')

    success, msg = SafetyService.resolve_report(report_id, admin_id, resolution, notes)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('admin.safety_detail', report_id=report_id))

@admin_bp.route('/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    """Security and operational audit trail."""
    logs = AuditService.get_all_logs(limit=250)
    return render_template('admin/audit_logs.html', active_page='audit', logs=logs)

@admin_bp.route('/backups')
@login_required
@role_required('admin')
def backups():
    """JSON storage backup snapshot manager."""
    backup_list = BackupService.list_backups()
    return render_template('admin/backups.html', active_page='backups', backups=backup_list)

@admin_bp.route('/backups/create', methods=['POST'])
@login_required
@role_required('admin')
def create_backup():
    """Trigger on-demand JSON database snapshot backup."""
    filename = BackupService.create_backup()
    AuditService.log_event(
        action="CREATE_BACKUP",
        resource_type="backup",
        details=f"Created backup archive: {filename}"
    )
    flash(f"Database snapshot created successfully: {filename}", "success")
    return redirect(url_for('admin.backups'))
