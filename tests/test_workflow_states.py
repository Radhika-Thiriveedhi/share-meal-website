from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.request_service import RequestService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_full_request_lifecycle_states(test_storage, test_data_dir):
    # Register Donor, Org, Volunteer
    _, _, donor = AuthService.register_user("chef@bistro.com", "ValidPass@123", "Chef", "donor")
    _, _, org = AuthService.register_user("shelter@ngo.org", "ValidPass@123", "Shelter", "organization")
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, org["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Fresh Baked Rolls",
        "food_category": "bakery_bread",
        "quantity_published": 50.0,
        "unit": "packages",
        "preparation_datetime": (now - timedelta(hours=2)).isoformat(),
        "collection_deadline": (now + timedelta(hours=10)).isoformat(),
        "storage_conditions": "room_temperature",
        "packaging_condition": "sealed_commercial",
        "allergens": ["Gluten (Wheat, Barley, Rye)"],
        "pickup_address": "400 Baker St"
    }
    _, _, don = DonationService.create_donation(donor["id"], donation_data)
    assert don["status"] == "available"

    # Request created -> status request_received
    _, _, req = RequestService.create_request(org["id"], don["id"], 50.0)
    assert req["status"] == "pending"

    # Donor approves -> status approved & donation confirmed
    RequestService.approve_request(req["id"], donor["id"])
    updated_req = RequestService.get_request_by_id(req["id"])
    assert updated_req["status"] == "approved"
    
    updated_don = DonationService.get_donation_by_id(don["id"])
    assert updated_don["status"] == "confirmed"
    assert updated_don["quantity_reserved"] == 50.0
    assert updated_don["quantity_available"] == 0.0
