from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_admin_user_verification_and_suspension(test_storage, test_data_dir):
    # Setup Admin & Pending Donor
    _, _, admin = AuthService.register_user("admin_core@sharemeal.org", "AdminPass@123", "Lead Admin", "admin")
    _, _, donor = AuthService.register_user("pending_bistro@food.com", "ValidPass@123", "Chef Pending", "donor")
    storage.update(Config.USERS_FILE, admin["id"], {"verification_status": "verified"})

    assert donor["verification_status"] == "pending"

    # 1. Admin approves verification
    storage.update(Config.USERS_FILE, donor["id"], {
        "verification_status": "verified",
        "verified_by": admin["name"]
    })
    verified_user = storage.find_by_id(Config.USERS_FILE, donor["id"])
    assert verified_user["verification_status"] == "verified"
    assert verified_user["verified_by"] == admin["name"]

    # 2. Admin suspends user
    storage.update(Config.USERS_FILE, donor["id"], {"is_active": False})
    suspended_user = storage.find_by_id(Config.USERS_FILE, donor["id"])
    assert suspended_user["is_active"] is False

    # 3. Suspended user cannot authenticate
    auth_success, auth_msg, _ = AuthService.authenticate("pending_bistro@food.com", "ValidPass@123")
    assert auth_success is False
    assert "suspended" in auth_msg
