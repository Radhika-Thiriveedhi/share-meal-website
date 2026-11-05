from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.request_service import RequestService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_atomic_reservation_and_over_reservation_prevention(test_storage, test_data_dir):
    # Setup Donor
    _, _, donor = AuthService.register_user(
        email="donor_res@bistro.com",
        password="ValidPassword@123",
        name="Chef Anton",
        role="donor",
        org_name="Anton Bistro",
        org_type="restaurant"
    )
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})

    # Setup 2 Orgs
    _, _, org1 = AuthService.register_user(
        email="shelter1@charity.org",
        password="ValidPassword@123",
        name="Shelter 1 Director",
        role="organization",
        org_name="Shelter One"
    )
    _, _, org2 = AuthService.register_user(
        email="shelter2@charity.org",
        password="ValidPassword@123",
        name="Shelter 2 Director",
        role="organization",
        org_name="Shelter Two"
    )
    storage.update(Config.USERS_FILE, org1["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, org2["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Roasted Chicken Portions",
        "food_category": "cooked_meals",
        "quantity_published": 100.0,
        "unit": "portions",
        "preparation_datetime": (now - timedelta(hours=1)).isoformat(),
        "collection_deadline": (now + timedelta(hours=8)).isoformat(),
        "storage_conditions": "hot_held",
        "packaging_condition": "food_grade_containers",
        "allergens": ["None declared / allergen-free"],
        "pickup_address": "100 Broadway"
    }
    _, _, don = DonationService.create_donation(donor["id"], donation_data)

    # 1. Org 1 requests 60 portions
    _, _, req1 = RequestService.create_request(org1["id"], don["id"], 60.0)
    # Donor approves
    app1_success, _ = RequestService.approve_request(req1["id"], donor["id"])
    assert app1_success is True

    updated_don = DonationService.get_donation_by_id(don["id"])
    assert updated_don["quantity_reserved"] == 60.0
    assert updated_don["quantity_available"] == 40.0
    assert updated_don["status"] == "partially_fulfilled"

    # 2. Org 2 attempts to request 50 portions (exceeds 40 available)
    fail_success, fail_msg, _ = RequestService.create_request(org2["id"], don["id"], 50.0)
    assert fail_success is False
    assert "exceeds" in fail_msg

    # 3. Org 2 requests exact remaining 40 portions
    _, _, req2 = RequestService.create_request(org2["id"], don["id"], 40.0)
    app2_success, _ = RequestService.approve_request(req2["id"], donor["id"])
    assert app2_success is True

    fully_reserved_don = DonationService.get_donation_by_id(don["id"])
    assert fully_reserved_don["quantity_reserved"] == 100.0
    assert fully_reserved_don["quantity_available"] == 0.0
    assert fully_reserved_don["status"] == "confirmed"

    # 4. Org 1 cancels request for 60 portions
    cancel_success, _ = RequestService.cancel_request(req1["id"], org1["id"])
    assert cancel_success is True

    released_don = DonationService.get_donation_by_id(don["id"])
    assert released_don["quantity_reserved"] == 40.0
    assert released_don["quantity_available"] == 60.0
    assert released_don["status"] == "available"
