import pytest
from services.analytics_service import AnalyticsService
from services.donation_service import DonationService
from services.request_service import RequestService
from storage.json_storage import storage
from config import Config

def test_analytics_summary_empty(test_data_dir):
    """Verify metrics calculate correctly on empty database."""
    summary = AnalyticsService.get_summary_metrics()
    assert summary["total_published"] == 0
    assert summary["total_distributed"] == 0
    assert summary["total_reserved"] == 0
    assert summary["total_available"] == 0
    assert summary["completed_collections"] == 0
    assert summary["active_volunteers"] == 0
    assert summary["co2_saved_kg"] == 0.0

def test_analytics_metrics_with_data(test_data_dir):
    """Verify live calculation of published, reserved, and distributed quantities."""
    # Seed donor and org users
    donor = {
        "id": "donor_test_1",
        "name": "Baker Jane",
        "org_name": "Harvest Bakery",
        "role": "donor",
        "is_verified": True,
        "is_active": True,
        "phone": "555-0123",
        "address": "123 Baker St"
    }
    org = {
        "id": "org_test_1",
        "name": "Director John",
        "org_name": "Shelter Outreach",
        "role": "organization",
        "is_verified": True,
        "is_active": True,
        "phone": "555-9999"
    }
    storage.insert(Config.USERS_FILE, donor)
    storage.insert(Config.USERS_FILE, org)

    # Create test donation with valid category key
    donation_data = {
        "food_name": "Artisan Sourdough Loaves",
        "food_category": "bakery_bread",
        "quantity_published": 50,
        "unit": "portions",
        "preparation_datetime": "2026-11-05T08:00",
        "collection_deadline": "2026-11-06T18:00",
        "storage_conditions": "room_temperature",
        "packaging_condition": "food_grade_containers",
        "pickup_address": "123 Baker St",
        "allergens": ["Gluten"]
    }
    success, errors, donation = DonationService.create_donation("donor_test_1", donation_data)
    assert success is True
    assert donation is not None

    # Check metrics after creation
    m1 = AnalyticsService.get_summary_metrics()
    assert m1["total_published"] == 50
    assert m1["total_available"] == 50
    assert m1["total_reserved"] == 0
    assert m1["total_distributed"] == 0

    # Reserve 20 portions via request
    req_success, msg, req = RequestService.create_request(
        organization_id="org_test_1",
        donation_id=donation["id"],
        quantity_requested=20,
        intended_beneficiaries="Shelter dinner"
    )
    assert req_success is True
    app_success, app_msg = RequestService.approve_request(req["id"], "donor_test_1")
    assert app_success is True

    # Metrics after approval: 20 reserved, 30 available
    m2 = AnalyticsService.get_summary_metrics()
    assert m2["total_published"] == 50
    assert m2["total_reserved"] == 20
    assert m2["total_available"] == 30
    assert m2["pending_requests"] == 0

    # Category breakdown test
    breakdown = AnalyticsService.get_category_breakdown()
    bakery_item = next((b for b in breakdown if b["label"] == "Bakery"), None)
    assert bakery_item is not None
    assert bakery_item["value"] == 50

def test_analytics_csv_export(test_data_dir):
    """Verify CSV string generation formats correctly."""
    donor = {
        "id": "donor_csv",
        "name": "Grocer Bob",
        "org_name": "City Grocer",
        "role": "donor",
        "is_verified": True,
        "is_active": True
    }
    storage.insert(Config.USERS_FILE, donor)

    donation_data = {
        "food_name": "Organic Apples",
        "food_category": "fresh_produce",
        "quantity_published": 30,
        "unit": "kg",
        "preparation_datetime": "2026-11-05T09:00",
        "collection_deadline": "2026-11-07T12:00",
        "storage_conditions": "refrigerated",
        "packaging_condition": "food_grade_containers",
        "pickup_address": "456 Market St",
        "allergens": []
    }
    DonationService.create_donation("donor_csv", donation_data)

    csv_content = AnalyticsService.generate_donations_csv()
    assert "Donation ID" in csv_content
    assert "City Grocer" in csv_content
    assert "Organic Apples" in csv_content
    assert "fresh_produce" in csv_content
