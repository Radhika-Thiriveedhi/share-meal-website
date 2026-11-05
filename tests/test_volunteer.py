from datetime import datetime, timedelta
from services.donation_service import DonationService
from services.request_service import RequestService
from services.volunteer_service import VolunteerService
from services.auth_service import AuthService
from storage.json_storage import storage
from config import Config

def test_volunteer_workflow_pickup_and_delivery(test_storage, test_data_dir):
    # Setup Donor, Org, Volunteer
    _, _, donor = AuthService.register_user("chef_v@kitchen.com", "ValidPass@123", "Chef Vol", "donor")
    _, _, org = AuthService.register_user("org_v@shelter.org", "ValidPass@123", "Director Vol", "organization")
    _, _, vol = AuthService.register_user("courier@transport.org", "ValidPass@123", "Courier Vol", "volunteer")
    storage.update(Config.USERS_FILE, donor["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, org["id"], {"verification_status": "verified"})
    storage.update(Config.USERS_FILE, vol["id"], {"verification_status": "verified"})

    now = datetime.utcnow()
    donation_data = {
        "food_name": "Hot Roasted Vegetables",
        "food_category": "cooked_meals",
        "quantity_published": 40.0,
        "unit": "portions",
        "preparation_datetime": (now - timedelta(hours=1)).isoformat(),
        "collection_deadline": (now + timedelta(hours=6)).isoformat(),
        "storage_conditions": "hot_held",
        "packaging_condition": "food_grade_containers",
        "allergens": ["None declared / allergen-free"],
        "pickup_address": "55 Civic Center"
    }
    _, _, don = DonationService.create_donation(donor["id"], donation_data)

    # Org requests and donor approves
    _, _, req = RequestService.create_request(org["id"], don["id"], 40.0)
    RequestService.approve_request(req["id"], donor["id"])

    # 1. Check available tasks
    tasks = VolunteerService.get_available_tasks()
    matching_task = next((t for t in tasks if t["id"] == req["id"]), None)
    assert matching_task is not None

    # 2. Volunteer accepts task
    accept_success, _ = VolunteerService.accept_task(req["id"], vol["id"])
    assert accept_success is True

    assigned_req = RequestService.get_request_by_id(req["id"])
    assert assigned_req["status"] == "volunteer_assigned"
    assert assigned_req["volunteer_id"] == vol["id"]

    # 3. Volunteer confirms pickup
    pickup_success, _ = VolunteerService.confirm_pickup(req["id"], vol["id"], "Inspected and packed hot")
    assert pickup_success is True

    picked_req = RequestService.get_request_by_id(req["id"])
    assert picked_req["status"] == "picked_up"
    assert picked_req["pickup_time"] is not None

    # 4. Volunteer confirms delivery
    deliver_success, _ = VolunteerService.confirm_delivery(req["id"], vol["id"], "Handed off to shelter staff")
    assert deliver_success is True

    delivered_req = RequestService.get_request_by_id(req["id"])
    assert delivered_req["status"] == "delivered"
    assert delivered_req["delivered_time"] is not None
