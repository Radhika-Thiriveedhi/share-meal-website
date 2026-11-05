from datetime import datetime
from storage.json_storage import storage
from storage.models import DonationModel
from utils.date_helpers import parse_iso, is_expired
from utils.validators import validate_donation_input
from services.audit_service import AuditService
from services.notification_service import NotificationService
from config import Config

class DonationService:
    @staticmethod
    def create_donation(donor_id, data):
        """Create a new food donation listing with full food safety fields."""
        valid, errors = validate_donation_input(data)
        if not valid:
            return False, errors, None

        donor = storage.find_by_id(Config.USERS_FILE, donor_id)
        if not donor:
            return False, {"donor": "Donor profile not found."}, None

        # Build model
        allergens = data.get('allergens', [])
        if isinstance(allergens, str):
            allergens = [allergens]

        donation = DonationModel.create(
            donor_id=donor_id,
            donor_name=donor.get('org_name') or donor.get('name'),
            donor_type=donor.get('org_type', 'restaurant'),
            donor_phone=donor.get('phone', ''),
            donor_address=donor.get('address', ''),
            food_name=data.get('food_name'),
            food_category=data.get('food_category'),
            quantity_published=data.get('quantity_published'),
            unit=data.get('unit'),
            preparation_datetime=data.get('preparation_datetime'),
            collection_deadline=data.get('collection_deadline'),
            storage_conditions=data.get('storage_conditions'),
            allergens=allergens,
            packaging_condition=data.get('packaging_condition'),
            pickup_address=data.get('pickup_address'),
            pickup_instructions=data.get('pickup_instructions', ''),
            special_handling_notes=data.get('special_handling_notes', '')
        )

        storage.insert(Config.DONATIONS_FILE, donation)

        AuditService.log_event(
            action="CREATE_DONATION",
            resource_type="donation",
            resource_id=donation["id"],
            details=f"Published {donation['quantity_published']} {donation['unit']} of {donation['food_name']}"
        )

        # Notify nearby receiving organizations
        NotificationService.notify_role(
            role="organization",
            title="New Surplus Food Available",
            message=f"{donation['donor_name']} published {donation['quantity_published']} {donation['unit']} of {donation['food_name']}.",
            notif_type="info",
            link="/org/browse"
        )

        return True, "Food donation published successfully.", donation

    @staticmethod
    def get_donor_donations(donor_id):
        """Retrieve all donations created by a specific donor."""
        DonationService.sweep_expired_donations()
        donations = storage.find_where(Config.DONATIONS_FILE, lambda d: d.get("donor_id") == donor_id)
        donations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return donations

    @staticmethod
    def get_donation_by_id(donation_id):
        """Find a donation by ID."""
        DonationService.sweep_expired_donations()
        return storage.find_by_id(Config.DONATIONS_FILE, donation_id)

    @staticmethod
    def update_donation(donation_id, donor_id, updates):
        """
        Edit an existing donation if eligible (e.g. no active approved requests).
        """
        donation = storage.find_by_id(Config.DONATIONS_FILE, donation_id)
        if not donation or donation.get('donor_id') != donor_id:
            return False, "Donation not found or unauthorized."

        if donation.get('status') in ['completed', 'cancelled', 'expired', 'safety_review']:
            return False, f"Cannot edit donation in '{donation.get('status')}' status."

        if float(donation.get('quantity_reserved', 0)) > 0:
            return False, "Cannot edit donation after portions have already been reserved by an organization."

        allowed_fields = [
            'food_name', 'food_category', 'quantity_published', 'unit',
            'preparation_datetime', 'collection_deadline', 'storage_conditions',
            'allergens', 'packaging_condition', 'pickup_address',
            'pickup_instructions', 'special_handling_notes'
        ]
        clean_updates = {k: updates[k] for k in allowed_fields if k in updates}
        
        if 'quantity_published' in clean_updates:
            qty = float(clean_updates['quantity_published'])
            clean_updates['quantity_available'] = qty

        updated = storage.update(Config.DONATIONS_FILE, donation_id, clean_updates)
        AuditService.log_event(
            action="UPDATE_DONATION",
            resource_type="donation",
            resource_id=donation_id,
            details=f"Updated listing details"
        )
        return True, "Donation updated successfully."

    @staticmethod
    def cancel_donation(donation_id, donor_id, reason="Donor cancellation"):
        """Cancel an eligible donation and release any pending requests."""
        donation = storage.find_by_id(Config.DONATIONS_FILE, donation_id)
        if not donation or donation.get('donor_id') != donor_id:
            return False, "Donation not found or unauthorized."

        if donation.get('status') in ['completed', 'picked_up']:
            return False, "Cannot cancel a donation that is already picked up or completed."

        storage.update(Config.DONATIONS_FILE, donation_id, {
            "status": "cancelled",
            "quantity_available": 0.0,
            "cancellation_reason": reason
        })

        # Cancel any pending requests associated with this donation
        requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get("donation_id") == donation_id and r.get("status") in ["pending", "approved"])
        for req in requests:
            storage.update(Config.REQUESTS_FILE, req["id"], {
                "status": "cancelled",
                "rejection_reason": f"Donation cancelled by donor: {reason}"
            })
            NotificationService.send_notification(
                user_id=req["organization_id"],
                title="Donation Cancelled by Donor",
                message=f"The listing for '{donation['food_name']}' was cancelled by the donor.",
                notif_type="warning"
            )

        AuditService.log_event(
            action="CANCEL_DONATION",
            resource_type="donation",
            resource_id=donation_id,
            details=f"Cancelled donation: {reason}"
        )
        return True, "Donation cancelled successfully."

    @staticmethod
    def sweep_expired_donations():
        """Automatically transition past-deadline donations to expired."""
        donations = storage.find_all(Config.DONATIONS_FILE)
        updated_any = False
        now = datetime.utcnow()

        for d in donations:
            if d.get('status') in ['available', 'request_received']:
                deadline = parse_iso(d.get('collection_deadline'))
                if deadline and now > deadline:
                    d['status'] = 'expired'
                    d['quantity_available'] = 0.0
                    updated_any = True

        if updated_any:
            storage.write(Config.DONATIONS_FILE, donations)
