import os
from datetime import datetime, timedelta
from utils.security import hash_password
from config import Config
from storage.json_storage import storage
from storage.models import UserModel, DonationModel, RequestModel, SafetyReportModel, NotificationModel, AuditLogModel

def seed_database(force=False):
    """
    Populate the JSON files with realistic, production-grade sample data
    demonstrating all four user roles and every donation lifecycle state.
    """
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Check if database already has users
    existing_users = storage.find_all(Config.USERS_FILE)
    if existing_users and not force:
        print("[Seed] Storage already populated. Skipping seed.")
        return False

    print("[Seed] Seeding realistic sample dataset for ShareMeal...")
    now = datetime.utcnow()

    # 1. USERS
    users = [
        # Platform Administrator
        UserModel.create(
            email="admin@sharemeal.org",
            password_hash=hash_password("Admin@123"),
            name="Sarah Jenkins (Lead Administrator)",
            role="admin",
            phone="+1 (555) 019-2831",
            address="100 Metro Civic Center, Suite 400",
            city="Metropolis",
            postal_code="94103",
            verification_status="verified",
            is_active=True
        ),
        
        # Donors (Verified)
        UserModel.create(
            email="greenbites@restaurant.com",
            password_hash=hash_password("Donor@123"),
            name="Marcus Vance",
            role="donor",
            phone="+1 (555) 234-5678",
            address="452 Culinary Boulevard",
            city="Metropolis",
            postal_code="94102",
            org_type="restaurant",
            org_name="GreenBites Bistro",
            license_number="FDB-2024-8841",
            tax_id="TAX-9948210",
            operating_hours="10:00 AM - 11:00 PM Daily",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="artisano@bakery.com",
            password_hash=hash_password("Donor@123"),
            name="Claire Dubois",
            role="donor",
            phone="+1 (555) 876-5432",
            address="120 Artisan Way",
            city="Metropolis",
            postal_code="94105",
            org_type="bakery",
            org_name="Artisano Craft Bakery & Cafe",
            license_number="FDB-2023-3490",
            tax_id="TAX-8831902",
            operating_hours="06:00 AM - 07:00 PM Tue-Sun",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="freshmart@groceries.com",
            password_hash=hash_password("Donor@123"),
            name="David Chen",
            role="donor",
            phone="+1 (555) 345-6789",
            address="800 Commercial Avenue",
            city="Metropolis",
            postal_code="94107",
            org_type="supermarket",
            org_name="Metro Fresh Supermarket",
            license_number="FDB-2022-1102",
            tax_id="TAX-7729103",
            operating_hours="07:00 AM - 10:00 PM Daily",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="grandpalace@events.com",
            password_hash=hash_password("Donor@123"),
            name="Elena Rostova",
            role="donor",
            phone="+1 (555) 456-7890",
            address="950 Grandview Heights",
            city="Metropolis",
            postal_code="94108",
            org_type="event_organizer",
            org_name="Grand Palace Banquet Center",
            license_number="FDB-2024-9042",
            tax_id="TAX-6610394",
            operating_hours="09:00 AM - Midnight On Events",
            verification_status="verified",
            is_active=True
        ),

        # Receiving Organizations (Verified)
        UserModel.create(
            email="hopehaven@shelter.org",
            password_hash=hash_password("Org@123"),
            name="Pastor Robert Miller",
            role="organization",
            phone="+1 (555) 567-8901",
            address="320 Shelter Haven Way",
            city="Metropolis",
            postal_code="94109",
            org_type="shelter",
            org_name="Hope Haven Emergency Shelter",
            license_number="NGO-501C3-1994",
            tax_id="TAX-5520194",
            operating_hours="24/7 Operations",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="nourishall@ngo.org",
            password_hash=hash_password("Org@123"),
            name="Dr. Anita Patel",
            role="organization",
            phone="+1 (555) 678-9012",
            address="510 Unity Plaza",
            city="Metropolis",
            postal_code="94110",
            org_type="ngo",
            org_name="NourishAll Community Relief Foundation",
            license_number="NGO-501C3-2015",
            tax_id="TAX-4439201",
            operating_hours="08:00 AM - 06:00 PM Mon-Sat",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="citykitchen@charity.org",
            password_hash=hash_password("Org@123"),
            name="Frank Gallagher",
            role="organization",
            phone="+1 (555) 789-0123",
            address="214 Mission Street",
            city="Metropolis",
            postal_code="94103",
            org_type="community_kitchen",
            org_name="City Central Soup Kitchen",
            license_number="NGO-501C3-2008",
            tax_id="TAX-3349102",
            operating_hours="06:00 AM - 08:00 PM Daily",
            verification_status="verified",
            is_active=True
        ),

        # Volunteers (Verified)
        UserModel.create(
            email="alex.v@volunteer.org",
            password_hash=hash_password("Vol@123"),
            name="Alex Rivera",
            role="volunteer",
            phone="+1 (555) 890-1234",
            address="142 Pine Street, Apt 3B",
            city="Metropolis",
            postal_code="94104",
            verification_status="verified",
            is_active=True
        ),
        UserModel.create(
            email="maya.s@volunteer.org",
            password_hash=hash_password("Vol@123"),
            name="Maya Sharma",
            role="volunteer",
            phone="+1 (555) 901-2345",
            address="784 Market St",
            city="Metropolis",
            postal_code="94102",
            verification_status="verified",
            is_active=True
        ),

        # Pending Users (for Admin Verification demonstration)
        UserModel.create(
            email="sunsetcafe@donor.com",
            password_hash=hash_password("Donor@123"),
            name="Liam O'Connor",
            role="donor",
            phone="+1 (555) 912-3456",
            address="67 Sunset Boulevard",
            city="Metropolis",
            postal_code="94116",
            org_type="restaurant",
            org_name="Sunset Coastal Cafe",
            license_number="FDB-PENDING-991",
            tax_id="TAX-1102948",
            operating_hours="07:00 AM - 04:00 PM Daily",
            verification_status="pending",
            is_active=True
        ),
        UserModel.create(
            email="safeharbor@org.com",
            password_hash=hash_password("Org@123"),
            name="Grace Henderson",
            role="organization",
            phone="+1 (555) 923-4567",
            address="89 Harbor Light Way",
            city="Metropolis",
            postal_code="94118",
            org_type="shelter",
            org_name="Safe Harbor Youth Center",
            license_number="NGO-PENDING-442",
            tax_id="TAX-2291048",
            operating_hours="24 Hours",
            verification_status="pending",
            is_active=True
        )
    ]
    storage.write(Config.USERS_FILE, users)

    # Reference IDs
    donor_greenbites = next(u for u in users if u["email"] == "greenbites@restaurant.com")
    donor_artisano = next(u for u in users if u["email"] == "artisano@bakery.com")
    donor_freshmart = next(u for u in users if u["email"] == "freshmart@groceries.com")
    donor_grandpalace = next(u for u in users if u["email"] == "grandpalace@events.com")

    org_hopehaven = next(u for u in users if u["email"] == "hopehaven@shelter.org")
    org_nourishall = next(u for u in users if u["email"] == "nourishall@ngo.org")
    org_citykitchen = next(u for u in users if u["email"] == "citykitchen@charity.org")

    vol_alex = next(u for u in users if u["email"] == "alex.v@volunteer.org")
    vol_maya = next(u for u in users if u["email"] == "maya.s@volunteer.org")

    # 2. DONATIONS
    donations = [
        # Available listing 1
        DonationModel.create(
            donor_id=donor_greenbites["id"],
            donor_name=donor_greenbites["org_name"],
            donor_type="restaurant",
            donor_phone=donor_greenbites["phone"],
            donor_address=donor_greenbites["address"],
            food_name="Mediterranean Grilled Chicken & Steamed Vegetables",
            food_category="cooked_meals",
            quantity_published=45.0,
            unit="portions",
            preparation_datetime=(now - timedelta(hours=3)).isoformat(),
            collection_deadline=(now + timedelta(hours=5)).isoformat(),
            storage_conditions="hot_held",
            allergens=["None declared / allergen-free"],
            packaging_condition="food_grade_containers",
            pickup_address="452 Culinary Boulevard, Metropolis",
            pickup_instructions="Loading dock located at rear alleyway. Ring Kitchen Bell B.",
            special_handling_notes="Must remain in insulated thermal containers above 60°C until distribution."
        ),
        # Available listing 2
        DonationModel.create(
            donor_id=donor_artisano["id"],
            donor_name=donor_artisano["org_name"],
            donor_type="bakery",
            donor_phone=donor_artisano["phone"],
            donor_address=donor_artisano["address"],
            food_name="Artisan Sourdough Loaves & Whole Grain Breads",
            food_category="bakery_bread",
            quantity_published=60.0,
            unit="packages",
            preparation_datetime=(now - timedelta(hours=8)).isoformat(),
            collection_deadline=(now + timedelta(hours=28)).isoformat(),
            storage_conditions="room_temperature",
            allergens=["Gluten (Wheat, Barley, Rye)"],
            packaging_condition="individually_wrapped",
            pickup_address="120 Artisan Way, Metropolis",
            pickup_instructions="Front counter entrance. Ask for Manager Claire.",
            special_handling_notes="Baked fresh this morning, keep dry and away from humidity."
        ),
        # Available listing 3
        DonationModel.create(
            donor_id=donor_freshmart["id"],
            donor_name=donor_freshmart["org_name"],
            donor_type="supermarket",
            donor_phone=donor_freshmart["phone"],
            donor_address=donor_freshmart["address"],
            food_name="Organic Apples, Pears, and Baby Spinach Crates",
            food_category="fresh_produce",
            quantity_published=120.0,
            unit="kg",
            preparation_datetime=(now - timedelta(hours=14)).isoformat(),
            collection_deadline=(now + timedelta(hours=36)).isoformat(),
            storage_conditions="refrigerated",
            allergens=["None declared / allergen-free"],
            packaging_condition="food_grade_containers",
            pickup_address="800 Commercial Avenue, Metropolis",
            pickup_instructions="Produce receiving door #3. Electric pallet jack available.",
            special_handling_notes="Clean surplus produce. Keep chilled between 2°C and 4°C."
        ),
        # Active Request In Progress (Confirmed / Volunteer Assigned)
        DonationModel.create(
            donor_id=donor_grandpalace["id"],
            donor_name=donor_grandpalace["org_name"],
            donor_type="event_organizer",
            donor_phone=donor_grandpalace["phone"],
            donor_address=donor_grandpalace["address"],
            food_name="Chilled Roasted Beef Sirloin & Baby Red Potatoes",
            food_category="cooked_meals",
            quantity_published=50.0,
            unit="portions",
            preparation_datetime=(now - timedelta(hours=5)).isoformat(),
            collection_deadline=(now + timedelta(hours=4)).isoformat(),
            storage_conditions="refrigerated",
            allergens=["Dairy & Lactose"],
            packaging_condition="insulated_boxes",
            pickup_address="950 Grandview Heights, Metropolis",
            pickup_instructions="Banquet service entrance. Check in with security desk.",
            special_handling_notes="Rapidly chilled following dinner gala. Maintained under 4°C."
        ),
        # Under Safety Review (Quarantined)
        DonationModel.create(
            donor_id=donor_greenbites["id"],
            donor_name=donor_greenbites["org_name"],
            donor_type="restaurant",
            donor_phone=donor_greenbites["phone"],
            donor_address=donor_greenbites["address"],
            food_name="Creamy Wild Mushroom Chowder",
            food_category="cooked_meals",
            quantity_published=30.0,
            unit="liters",
            preparation_datetime=(now - timedelta(hours=12)).isoformat(),
            collection_deadline=(now + timedelta(hours=6)).isoformat(),
            storage_conditions="hot_held",
            allergens=["Dairy & Lactose", "Gluten (Wheat, Barley, Rye)"],
            packaging_condition="food_grade_containers",
            pickup_address="452 Culinary Boulevard, Metropolis",
            pickup_instructions="Kitchen door B",
            special_handling_notes="Temperature holding issue flagged during routine check."
        ),
        # Completed / Distributed donation
        DonationModel.create(
            donor_id=donor_artisano["id"],
            donor_name=donor_artisano["org_name"],
            donor_type="bakery",
            donor_phone=donor_artisano["phone"],
            donor_address=donor_artisano["address"],
            food_name="Assorted French Croissants & Danish Pastries",
            food_category="bakery_bread",
            quantity_published=80.0,
            unit="packages",
            preparation_datetime=(now - timedelta(days=2, hours=6)).isoformat(),
            collection_deadline=(now - timedelta(days=1, hours=12)).isoformat(),
            storage_conditions="room_temperature",
            allergens=["Gluten (Wheat, Barley, Rye)", "Dairy & Lactose", "Eggs"],
            packaging_condition="food_grade_containers",
            pickup_address="120 Artisan Way, Metropolis",
            pickup_instructions="Front bakery counter",
            special_handling_notes="Fully collected and distributed yesterday."
        ),
        # Expired donation
        DonationModel.create(
            donor_id=donor_freshmart["id"],
            donor_name=donor_freshmart["org_name"],
            donor_type="supermarket",
            donor_phone=donor_freshmart["phone"],
            donor_address=donor_freshmart["address"],
            food_name="Fresh Cut Melons & Fruit Cups",
            food_category="fresh_produce",
            quantity_published=25.0,
            unit="packages",
            preparation_datetime=(now - timedelta(days=3)).isoformat(),
            collection_deadline=(now - timedelta(hours=12)).isoformat(),
            storage_conditions="refrigerated",
            allergens=["None declared / allergen-free"],
            packaging_condition="food_grade_containers",
            pickup_address="800 Commercial Avenue, Metropolis",
            pickup_instructions="Produce receiving door #3",
            special_handling_notes="Expired without collection. Safe disposal required."
        )
    ]

    # Adjust status for non-available donations
    donations[3]["status"] = "confirmed"
    donations[3]["quantity_reserved"] = 50.0
    donations[3]["quantity_available"] = 0.0

    donations[4]["status"] = "safety_review"
    donations[4]["safety_review_reason"] = "Reported temperature drop during hot-holding verification."

    donations[5]["status"] = "completed"
    donations[5]["quantity_reserved"] = 0.0
    donations[5]["quantity_distributed"] = 80.0
    donations[5]["quantity_available"] = 0.0

    donations[6]["status"] = "expired"
    donations[6]["quantity_available"] = 0.0

    storage.write(Config.DONATIONS_FILE, donations)

    # 3. REQUESTS
    requests = [
        # Request 1: Confirmed & Volunteer Assigned (for donation 3)
        RequestModel.create(
            donation_id=donations[3]["id"],
            organization_id=org_hopehaven["id"],
            organization_name=org_hopehaven["org_name"],
            organization_contact=f"{org_hopehaven['name']} ({org_hopehaven['phone']})",
            quantity_requested=50.0,
            urgency="urgent",
            intended_beneficiaries="Night shelter residents (approx 45 adults and youths)"
        ),
        # Request 2: Completed Request (for donation 5)
        RequestModel.create(
            donation_id=donations[5]["id"],
            organization_id=org_citykitchen["id"],
            organization_name=org_citykitchen["org_name"],
            organization_contact=f"{org_citykitchen['name']} ({org_citykitchen['phone']})",
            quantity_requested=80.0,
            urgency="normal",
            intended_beneficiaries="Morning community breakfast service"
        )
    ]

    # Setup progress for Request 1
    requests[0]["status"] = "volunteer_assigned"
    requests[0]["volunteer_id"] = vol_alex["id"]
    requests[0]["volunteer_name"] = vol_alex["name"]
    requests[0]["volunteer_phone"] = vol_alex["phone"]
    requests[0]["pickup_notes"] = "Volunteer en route with dual insulated temperature transport bags."

    # Setup progress for Request 2 (Completed)
    requests[1]["status"] = "receipt_confirmed"
    requests[1]["volunteer_id"] = vol_maya["id"]
    requests[1]["volunteer_name"] = vol_maya["name"]
    requests[1]["volunteer_phone"] = vol_maya["phone"]
    requests[1]["pickup_time"] = (now - timedelta(days=2)).isoformat()
    requests[1]["delivered_time"] = (now - timedelta(days=1, hours=22)).isoformat()
    requests[1]["confirmed_time"] = (now - timedelta(days=1, hours=20)).isoformat()
    requests[1]["recipient_feedback"] = "Excellent condition, bakery items were packaged carefully and served immediately."
    requests[1]["rating"] = 5

    storage.write(Config.REQUESTS_FILE, requests)

    # 4. SAFETY REPORT
    safety_reports = [
        SafetyReportModel.create(
            donation_id=donations[4]["id"],
            reporter_id=org_nourishall["id"],
            reporter_role="organization",
            reporter_name=org_nourishall["name"],
            report_type="temperature_abuse",
            description="Inspection upon initial arrival showed soup holding temperature had dropped to 48°C (minimum safe threshold is 60°C).",
            incident_time=(now - timedelta(hours=2)).isoformat()
        )
    ]
    storage.write(Config.SAFETY_REPORTS_FILE, safety_reports)

    # 5. NOTIFICATIONS
    notifications = [
        NotificationModel.create(
            user_id=donor_grandpalace["id"],
            title="Volunteer Assigned to Food Collection",
            message=f"Volunteer {vol_alex['name']} has accepted the dispatch for '{donations[3]['food_name']}'.",
            notif_type="info",
            link="/donor/requests"
        ),
        NotificationModel.create(
            user_id=vol_alex["id"],
            title="Dispatch Assignment Confirmed",
            message="You have been assigned to collect 50 portions from Grand Palace Banquet Center.",
            notif_type="success",
            link="/volunteer/dashboard"
        ),
        NotificationModel.create(
            user_id=org_hopehaven["id"],
            title="Food Request Approved by Donor",
            message="Grand Palace Banquet Center approved your request. Volunteer dispatch in progress.",
            notif_type="success",
            link="/org/requests"
        ),
        NotificationModel.create(
            user_id=donor_greenbites["id"],
            title="Safety Review Quarantine Initiated",
            message=f"Listing '{donations[4]['food_name']}' has been quarantined for admin temperature review.",
            notif_type="warning",
            link="/donor/donations"
        )
    ]
    storage.write(Config.NOTIFICATIONS_FILE, notifications)

    # 6. AUDIT LOGS
    audit_logs = [
        AuditLogModel.create(
            user_id=donor_greenbites["id"],
            user_email=donor_greenbites["email"],
            user_role="donor",
            action="CREATE_DONATION",
            resource_type="donation",
            resource_id=donations[0]["id"],
            details="Published 45 portions of Mediterranean Grilled Chicken."
        ),
        AuditLogModel.create(
            user_id=donor_grandpalace["id"],
            user_email=donor_grandpalace["email"],
            user_role="donor",
            action="APPROVE_REQUEST",
            resource_type="request",
            resource_id=requests[0]["id"],
            details="Approved 50 portions request from Hope Haven Emergency Shelter."
        ),
        AuditLogModel.create(
            user_id=vol_alex["id"],
            user_email=vol_alex["email"],
            user_role="volunteer",
            action="ACCEPT_TASK",
            resource_type="request",
            resource_id=requests[0]["id"],
            details="Accepted collection dispatch for Hope Haven."
        ),
        AuditLogModel.create(
            user_id=org_nourishall["id"],
            user_email=org_nourishall["email"],
            user_role="organization",
            action="REPORT_SAFETY",
            resource_type="safety_report",
            resource_id=safety_reports[0]["id"],
            details="Reported temperature holding non-compliance on Creamy Wild Mushroom Chowder."
        )
    ]
    storage.write(Config.AUDIT_LOGS_FILE, audit_logs)

    print("[Seed] Successfully initialized all 6 databases with rich realistic data.")
    return True

if __name__ == "__main__":
    seed_database(force=True)
