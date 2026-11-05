from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from services.notification_service import NotificationService
from utils.decorators import login_required

notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notification_bp.route('/')
@login_required
def index():
    """List all internal system notifications for the authenticated user."""
    user_id = session.get('user_id')
    notifications = NotificationService.get_user_notifications(user_id)
    return render_template('notifications/index.html', notifications=notifications)

@notification_bp.route('/<notif_id>/read')
@login_required
def mark_read(notif_id):
    """Mark a specific notification as read and redirect to its link if available."""
    user_id = session.get('user_id')
    notif = NotificationService.mark_as_read(notif_id, user_id)
    if notif and notif.get('link'):
        return redirect(notif['link'])
    return redirect(url_for('notifications.index'))

@notification_bp.route('/read-all')
@login_required
def mark_all_read():
    """Mark all unread notifications as read."""
    user_id = session.get('user_id')
    NotificationService.mark_all_as_read(user_id)
    flash("All notifications marked as read.", "info")
    return redirect(url_for('notifications.index'))
