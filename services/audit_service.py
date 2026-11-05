from flask import has_request_context, request, session
from storage.json_storage import storage
from storage.models import AuditLogModel
from config import Config

class AuditService:
    @staticmethod
    def log_event(action, resource_type, resource_id="", details="", user_id=None, user_email=None, user_role=None):
        """Record an operational or security audit log safely handling test and CLI environments."""
        if has_request_context():
            ip = request.remote_addr if request.remote_addr else "127.0.0.1"
            uid = user_id or session.get("user_id", "anonymous")
            email = user_email or session.get("email", "anonymous")
            role = user_role or session.get("role", "guest")
        else:
            ip = "127.0.0.1"
            uid = user_id or "system"
            email = user_email or "system"
            role = user_role or "system"

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
