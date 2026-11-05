import os
import zipfile
from services.backup_service import BackupService
from services.audit_service import AuditService
from storage.json_storage import storage
from config import Config

def test_audit_logging_and_retrieval(test_data_dir):
    """Verify audit events are recorded in audit_logs.json and retrieved chronologically."""
    AuditService.log_event(
        action="TEST_ACTION",
        resource_type="system",
        resource_id="res_123",
        details="Tested audit service logging",
        user_id="user_123",
        user_email="donor@example.com",
        user_role="donor"
    )

    logs = AuditService.get_all_logs(limit=10)
    assert len(logs) >= 1
    assert logs[0]["action"] == "TEST_ACTION"
    assert logs[0]["user_id"] == "user_123"
    assert logs[0]["user_email"] == "donor@example.com"

def test_backup_creation_and_listing(test_data_dir):
    """Verify creation of zip backup containing active JSON files."""
    # Ensure there's a JSON file to backup
    storage.insert(Config.USERS_FILE, {"id": "dummy_user", "email": "dummy@example.com"})

    backup_name = BackupService.create_backup()
    assert backup_name.startswith("sharemeal_backup_")
    assert backup_name.endswith(".zip")

    # Verify backup is listed
    backups = BackupService.list_backups()
    assert len(backups) >= 1
    assert backups[0]["filename"] == backup_name

    # Inspect zip contents
    backup_file_path = os.path.join(Config.BACKUP_DIR, backup_name)
    with zipfile.ZipFile(backup_file_path, 'r') as zf:
        namelist = zf.namelist()
        assert "users.json" in namelist
