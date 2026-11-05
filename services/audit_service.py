from flask import request, session
from storage.json_storage import storage
from storage.models import AuditLogModel
from config import Config

class AuditService:
    @staticmethod
    def log_event(action, resource_type, resource_id="", details="", user_id=None, user_email=None, user_role=None):
        """Record an operational or security audit log."""
        try:
            ip = request.remote_addr if request else "127.0.0.1"
        except RuntimeError:
            ip = "127.0.0.1"

        uid = user_id or session.get("user_id", "anonymous")
        email = user_email or session.get("email", "anonymous")
        role = user_role or session.get("role", "guest")

        log_entry = AuditLogModel.create(
            user_id=uid,
            user_email=email,
            user_role=role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip
        )
        storage.insert(Config.AUDIT_LOGS_FILE, log_entry)
        return log_entry

    @staticmethod
    def get_all_logs(limit=200):
        """Retrieve recent audit logs in reverse chronological order."""
        logs = storage.find_all(Config.AUDIT_LOGS_FILE)
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return logs[:limit]
