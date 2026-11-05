from storage.json_storage import storage
from storage.models import NotificationModel
from config import Config

class NotificationService:
    @staticmethod
    def send_notification(user_id, title, message, notif_type="info", link=""):
        """Create and queue an internal system notification for a specific user."""
        notif = NotificationModel.create(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=notif_type,
            link=link
        )
        storage.insert(Config.NOTIFICATIONS_FILE, notif)
        return notif

    @staticmethod
    def notify_role(role, title, message, notif_type="info", link=""):
        """Broadcast a notification to all verified users of a specific role."""
        users = storage.find_where(Config.USERS_FILE, lambda u: u.get("role") == role and u.get("is_active", True))
        sent = []
        for u in users:
            sent.append(NotificationService.send_notification(u["id"], title, message, notif_type, link))
        return sent

    @staticmethod
    def notify_admins(title, message, notif_type="warning", link=""):
        """Broadcast an alert to all platform administrators."""
        return NotificationService.notify_role("admin", title, message, notif_type, link)

    @staticmethod
    def get_user_notifications(user_id, limit=50):
        """Retrieve recent notifications for a user."""
        notifs = storage.find_where(Config.NOTIFICATIONS_FILE, lambda n: n.get("user_id") == user_id)
        notifs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return notifs[:limit]

    @staticmethod
    def get_unread_count(user_id):
        """Return the count of unread notifications for a user."""
        notifs = storage.find_where(Config.NOTIFICATIONS_FILE, lambda n: n.get("user_id") == user_id and not n.get("is_read", False))
        return len(notifs)

    @staticmethod
    def mark_as_read(notif_id, user_id):
        """Mark a notification as read if it belongs to the user."""
        notif = storage.find_by_id(Config.NOTIFICATIONS_FILE, notif_id)
        if notif and notif.get("user_id") == user_id:
            return storage.update(Config.NOTIFICATIONS_FILE, notif_id, {"is_read": True})
        return None

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all unread notifications for a user as read."""
        all_notifs = storage.find_all(Config.NOTIFICATIONS_FILE)
        updated_any = False
        for n in all_notifs:
            if n.get("user_id") == user_id and not n.get("is_read", False):
                n["is_read"] = True
                updated_any = True
        if updated_any:
            storage.write(Config.NOTIFICATIONS_FILE, all_notifs)
        return True
