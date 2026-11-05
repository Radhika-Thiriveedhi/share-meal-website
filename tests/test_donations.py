from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_create_and_cancel_donation(test_storage, test_data_dir):
    # Register test donor
    _, _, donor = AuthService.register_user(
        email="donor_chef@bistro.com",
        password="ValidPassword@123",
        name="Chef Pierre",
        role="donor",
        org_name="Pierre Bistro",
        org_type="restaurant"
    )
    # Mark verified for testing
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Vegetable Lasagna",
        "food_category": "cooked_meals",
        "quantity_published": 30.0,
        "unit": "portions",
        "preparation_datetime": (now - timedelta(hours=1)).isoformat(),
        "collection_deadline": (now + timedelta(hours=6)).isoformat(),
        "storage_conditions": "hot_held",
        "packaging_condition": "food_grade_containers",
        "allergens": ["Dairy & Lactose", "Gluten (Wheat, Barley, Rye)"],
        "pickup_address": "77 French Quarter"
    }

    success, msg, donation = DonationService.create_donation(donor["id"], donation_data)
    assert success is True
    assert donation["quantity_available"] == 30.0
    assert donation["status"] == "available"

    # Cancel donation
    cancel_success, _ = DonationService.cancel_donation(donation["id"], donor["id"], reason="Kitchen test")
    assert cancel_success is True

    cancelled_don = DonationService.get_donation_by_id(donation["id"])
    assert cancelled_don["status"] == "cancelled"
    assert cancelled_don["quantity_available"] == 0.0
