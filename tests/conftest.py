import os
import pytest
from config import Config
from storage.json_storage import JSONStorage

@pytest.fixture(autouse=True)
def test_data_dir(monkeypatch, tmp_path):
    """Automatically isolate all JSON storage files into a fresh temp directory for each test."""
    test_dir = str(tmp_path)
    monkeypatch.setattr(Config, "DATA_DIR", test_dir)
    monkeypatch.setattr(Config, "USERS_FILE", os.path.join(test_dir, "users.json"))
    monkeypatch.setattr(Config, "DONATIONS_FILE", os.path.join(test_dir, "donations.json"))
    monkeypatch.setattr(Config, "REQUESTS_FILE", os.path.join(test_dir, "requests.json"))
    monkeypatch.setattr(Config, "SAFETY_REPORTS_FILE", os.path.join(test_dir, "safety_reports.json"))
    monkeypatch.setattr(Config, "NOTIFICATIONS_FILE", os.path.join(test_dir, "notifications.json"))
    monkeypatch.setattr(Config, "AUDIT_LOGS_FILE", os.path.join(test_dir, "audit_logs.json"))
    monkeypatch.setattr(Config, "BACKUP_DIR", os.path.join(test_dir, "backups"))
    yield test_dir

@pytest.fixture
def test_storage(test_data_dir):
    """Provide an isolated JSONStorage instance for tests."""
    return JSONStorage(data_dir=test_data_dir)
