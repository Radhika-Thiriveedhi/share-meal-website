import pytest
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_register_and_authenticate(test_storage, test_data_dir):
    # Register Donor
    success, msg, user = AuthService.register_user(
        email="test_bistro@example.com",
        password="SecurePassword@123",
        name="Chef Alex",
        role="donor",
        org_name="Test Bistro",
        org_type="restaurant"
    )
    assert success is True
    assert user["role"] == "donor"
    assert user["verification_status"] == "pending"

    # Reject duplicate email
    dup_success, dup_msg, _ = AuthService.register_user(
        email="test_bistro@example.com",
        password="AnotherPassword@123",
        name="Copycat",
        role="donor"
    )
    assert dup_success is False
    assert "already exists" in dup_msg

def test_authenticate_invalid_credentials(test_storage):
    success, msg, user = AuthService.authenticate("nonexistent@example.com", "Password@123")
    assert success is False
    assert "Invalid email or password" in msg
