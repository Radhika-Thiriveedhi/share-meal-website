from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.safety_service import SafetyService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_safety_report_quarantine_and_resolution(test_storage, test_data_dir):
    # Setup Donor, Admin, Org
    _, _, admin = AuthService.register_user("admin_safe@sharemeal.org", "AdminPass@123", "Lead Auditor", "admin")
    _, _, donor = AuthService.register_user("donor_safe@kitchen.com", "ValidPass@123", "Chef Safe", "donor")
    _, _, org = AuthService.register_user("org_safe@shelter.org", "ValidPass@123", "Director Safe", "organization")
    storage.update(Config.USERS_FILE, admin["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, org["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Seafood Paella",
        "food_category": "cooked_meals",
        "quantity_published": 25.0,
        "unit": "portions",
        "preparation_datetime": (now - timedelta(hours=2)).isoformat(),
        "collection_deadline": (now + timedelta(hours=4)).isoformat(),
        "storage_conditions": "hot_held",
        "packaging_condition": "food_grade_containers",
        "allergens": ["Fish", "Shellfish & Crustaceans"],
        "pickup_address": "12 Harbor Pier"
    }
    _, _, don = DonationService.create_donation(donor["id"], donation_data)
    assert don["status"] == "available"

    # 1. File safety report -> donation automatically quarantined
    success, msg, report = SafetyService.file_report(
        donation_id=don["id"],
        reporter_id=org["id"],
        reporter_role="organization",
        reporter_name="Director Safe",
        report_type="temperature_abuse",
        description="Measured food holding temperature was 49°C, violating 60°C requirement."
    )
    assert success is True
    assert report["status"] == "under_review"

    quarantined_don = DonationService.get_donation_by_id(don["id"])
    assert quarantined_don["status"] == "safety_review"
    assert "Quarantined" in quarantined_don["safety_review_reason"]

    # 2. Admin resolves report as discarded (hazardous)
    res_success, res_msg = SafetyService.resolve_report(
        report_id=report["id"],
        admin_id=admin["id"],
        resolution="resolved_discarded",
        admin_notes="Confirmed temperature abuse; ordered kitchen safe disposal."
    )
    assert res_success is True

    resolved_rep = SafetyService.get_report_by_id(report["id"])
    assert resolved_rep["status"] == "resolved_discarded"

    discarded_don = DonationService.get_donation_by_id(don["id"])
    assert discarded_don["status"] == "cancelled"
    assert discarded_don["quantity_available"] == 0.0
