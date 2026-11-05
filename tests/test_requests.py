from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.request_service import RequestService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_create_and_cancel_request(test_storage, test_data_dir):
    # Setup Donor
    _, _, donor = AuthService.register_user(
        email="donor_req@kitchen.com",
        password="ValidPassword@123",
        name="Chef Maria",
        role="donor",
        org_name="Maria Kitchen",
        org_type="restaurant"
    )
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})

    # Setup Org
    _, _, org = AuthService.register_user(
        email="org_shelter@charity.org",
        password="ValidPassword@123",
        name="Sister Teresa",
        role="organization",
        org_name="Teresa Shelter",
        org_type="shelter"
    )
    storage.update(Config.USERS_FILE, org["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Warm Beef Stew",
        "food_category": "cooked_meals",
        "quantity_published": 50.0,
        "unit": "portions",
        "preparation_datetime": (now - timedelta(hours=1)).isoformat(),
        "collection_deadline": (now + timedelta(hours=5)).isoformat(),
        "storage_conditions": "hot_held",
        "packaging_condition": "food_grade_containers",
        "allergens": ["None declared / allergen-free"],
        "pickup_address": "88 Central Park"
    }
    _, _, don = DonationService.create_donation(donor["id"], donation_data)

    # 1. Partial request
    success, msg, req = RequestService.create_request(
        organization_id=org["id"],
        donation_id=don["id"],
        quantity_requested=20.0,
        urgency="urgent",
        intended_beneficiaries="20 homeless youths"
    )
    assert success is True
    assert req["quantity_requested"] == 20.0
    assert req["status"] == "pending"

    # 2. Over-capacity request should fail
    fail_success, fail_msg, _ = RequestService.create_request(
        organization_id=org["id"],
        donation_id=don["id"],
        quantity_requested=999.0
    )
    assert fail_success is False
    assert "exceeds" in fail_msg

    # 3. Cancel request
    cancel_success, _ = RequestService.cancel_request(req["id"], org["id"], reason="Test cancellation")
    assert cancel_success is True
    
    cancelled_req = RequestService.get_request_by_id(req["id"])
    assert cancelled_req["status"] == "cancelled"
