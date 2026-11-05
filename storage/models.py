import uuid
from datetime import datetime

def generate_id(prefix="item"):
    """Generate a clean human-readable unique ID."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class UserModel:
    @staticmethod
    def create(email, password_hash, name, role, phone="", address="", city="", postal_code="",
               org_type="", org_name="", license_number="", tax_id="", operating_hours="",
               verification_status="pending", is_active=True):
        now = datetime.utcnow().isoformat()
        return {
            "id": generate_id("usr"),
            "email": email.strip().lower(),
            "password_hash": password_hash,
            "name": name.strip(),
            "role": role,
            "phone": phone.strip(),
            "address": address.strip(),
            "city": city.strip(),
            "postal_code": postal_code.strip(),
            "org_type": org_type.strip(),
            "org_name": org_name.strip() if org_name else name.strip(),
            "license_number": license_number.strip(),
            "tax_id": tax_id.strip(),
            "operating_hours": operating_hours.strip(),
            "verification_status": verification_status,
            "verification_notes": "",
            "verified_at": now if verification_status == "verified" else None,
            "verified_by": "system" if verification_status == "verified" else None,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now
        }

class DonationModel:
    @staticmethod
    def create(donor_id, donor_name, donor_type, donor_phone, donor_address,
               food_name, food_category, quantity_published, unit,
               preparation_datetime, collection_deadline, storage_conditions,
               allergens, packaging_condition, pickup_address,
               pickup_instructions="", special_handling_notes=""):
        now = datetime.utcnow().isoformat()
        qty = float(quantity_published)
        return {
            "id": generate_id("don"),
            "donor_id": donor_id,
            "donor_name": donor_name,
            "donor_type": donor_type,
            "donor_phone": donor_phone,
            "donor_address": donor_address,
            "food_name": food_name.strip(),
            "food_category": food_category,
            "quantity_published": qty,
            "quantity_reserved": 0.0,
            "quantity_distributed": 0.0,
            "quantity_available": qty,
            "unit": unit,
            "preparation_datetime": preparation_datetime,
            "collection_deadline": collection_deadline,
            "storage_conditions": storage_conditions,
            "allergens": allergens if isinstance(allergens, list) else [allergens],
            "packaging_condition": packaging_condition,
            "pickup_address": pickup_address.strip(),
            "pickup_instructions": pickup_instructions.strip(),
            "special_handling_notes": special_handling_notes.strip(),
            "status": "available",
            "safety_review_reason": "",
            "created_at": now,
            "updated_at": now
        }

class RequestModel:
    @staticmethod
    def create(donation_id, organization_id, organization_name, organization_contact,
               quantity_requested, urgency="normal", intended_beneficiaries=""):
        now = datetime.utcnow().isoformat()
        return {
            "id": generate_id("req"),
            "donation_id": donation_id,
            "organization_id": organization_id,
            "organization_name": organization_name,
            "organization_contact": organization_contact,
            "quantity_requested": float(quantity_requested),
            "urgency": urgency,
            "intended_beneficiaries": intended_beneficiaries.strip(),
            "status": "pending",
            "rejection_reason": "",
            "volunteer_id": None,
            "volunteer_name": None,
            "volunteer_phone": None,
            "pickup_notes": "",
            "delivery_notes": "",
            "pickup_time": None,
            "delivered_time": None,
            "confirmed_time": None,
            "recipient_feedback": "",
            "rating": None,
            "created_at": now,
            "updated_at": now
        }

class SafetyReportModel:
    @staticmethod
    def create(donation_id, reporter_id, reporter_role, reporter_name,
               report_type, description, incident_time="", request_id=None):
        now = datetime.utcnow().isoformat()
        return {
            "id": generate_id("saf"),
            "donation_id": donation_id,
            "request_id": request_id,
            "reporter_id": reporter_id,
            "reporter_role": reporter_role,
            "reporter_name": reporter_name,
            "report_type": report_type,
            "description": description.strip(),
            "incident_time": incident_time or now,
            "status": "under_review",
            "admin_notes": "",
            "resolution": "",
            "reviewed_by": None,
            "reviewed_at": None,
            "created_at": now,
            "updated_at": now
        }

class NotificationModel:
    @staticmethod
    def create(user_id, title, message, notif_type="info", link=""):
        now = datetime.utcnow().isoformat()
        return {
            "id": generate_id("notif"),
            "user_id": user_id,
            "title": title.strip(),
            "message": message.strip(),
            "type": notif_type,
            "link": link.strip(),
            "is_read": False,
            "created_at": now
        }

class AuditLogModel:
    @staticmethod
    def create(user_id, user_email, user_role, action, resource_type, resource_id="", details="", ip_address="127.0.0.1"):
        now = datetime.utcnow().isoformat()
        return {
            "id": generate_id("log"),
            "user_id": user_id,
            "user_email": user_email,
            "user_role": user_role,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "timestamp": now
        }
