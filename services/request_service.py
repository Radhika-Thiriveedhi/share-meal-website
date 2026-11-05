from datetime import datetime
from storage.json_storage import storage
from storage.models import RequestModel
from utils.date_helpers import is_expired
from services.audit_service import AuditService
from services.notification_service import NotificationService
from services.donation_service import DonationService
from config import Config

class RequestService:
    @staticmethod
    def create_request(organization_id, donation_id, quantity_requested, urgency="normal", intended_beneficiaries=""):
        """
        Create a new request for food portions.
        Strictly validates that requested quantity <= donation.quantity_available
        and that the donation is active, not expired, and not in safety review.
        """
        DonationService.sweep_expired_donations()
        
        donation = storage.find_by_id(Config.DONATIONS_FILE, donation_id)
        if not donation:
            return False, "Donation listing not found.", None

        if donation.get("status") != "available" and donation.get("status") != "request_received" and donation.get("status") != "partially_fulfilled":
            return False, f"This donation is currently '{donation.get('status')}' and cannot accept requests.", None

        if is_expired(donation.get("collection_deadline")):
            storage.update(Config.DONATIONS_FILE, donation_id, {"status": "expired", "quantity_available": 0.0})
            return False, "The collection deadline for this food listing has expired.", None

        try:
            qty_req = float(quantity_requested)
            if qty_req <= 0:
                return False, "Requested quantity must be greater than zero.", None
        except (ValueError, TypeError):
            return False, "Please enter a valid numeric quantity.", None

        available_qty = float(donation.get("quantity_available", 0))
        if qty_req > available_qty:
            return False, f"Requested quantity ({qty_req} {donation.get('unit')}) exceeds currently available quantity ({available_qty} {donation.get('unit')}).", None

        org = storage.find_by_id(Config.USERS_FILE, organization_id)
        if not org:
            return False, "Requesting organization not found.", None

        req = RequestModel.create(
            donation_id=donation_id,
            organization_id=organization_id,
            organization_name=org.get("org_name") or org.get("name"),
            organization_contact=f"{org.get('name')} ({org.get('phone', 'N/A')})",
            quantity_requested=qty_req,
            urgency=urgency,
            intended_beneficiaries=intended_beneficiaries
        )
        storage.insert(Config.REQUESTS_FILE, req)

        # Update donation status to indicate a request is received
        storage.update(Config.DONATIONS_FILE, donation_id, {"status": "request_received"})

        AuditService.log_event(
            action="CREATE_REQUEST",
            resource_type="request",
            resource_id=req["id"],
            details=f"Requested {qty_req} {donation['unit']} of {donation['food_name']} for {org.get('org_name')}"
        )

        # Notify donor of incoming request
        NotificationService.send_notification(
            user_id=donation["donor_id"],
            title="New Food Request Received",
            message=f"{req['organization_name']} requested {qty_req} {donation['unit']} of '{donation['food_name']}'. Review and approve.",
            notif_type="warning",
            link="/donor/requests"
        )

        return True, "Food request submitted successfully. Awaiting donor confirmation.", req

    @staticmethod
    def get_organization_requests(org_id):
        """Get all requests submitted by an organization."""
        requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get("organization_id") == org_id)
        requests.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return requests

    @staticmethod
    def get_request_by_id(request_id):
        """Fetch request by ID."""
        return storage.find_by_id(Config.REQUESTS_FILE, request_id)

    @staticmethod
    def cancel_request(request_id, org_id, reason="Cancelled by organization"):
        """
        Cancel a pending or approved request.
        If approved, releases reserved quantity back to available.
        """
        req = storage.find_by_id(Config.REQUESTS_FILE, request_id)
        if not req or req.get("organization_id") != org_id:
            return False, "Request not found or unauthorized."

        if req.get("status") in ["picked_up", "delivered", "receipt_confirmed"]:
            return False, "Cannot cancel a request that is already picked up or delivered."

        prev_status = req.get("status")
        qty = float(req.get("quantity_requested", 0))

        # Update request
        storage.update(Config.REQUESTS_FILE, request_id, {
            "status": "cancelled",
            "rejection_reason": reason
        })

        # If previously approved, recalculate donation reserved and available quantities
        donation = storage.find_by_id(Config.DONATIONS_FILE, req.get("donation_id"))
        if donation and prev_status in ["approved", "volunteer_assigned"]:
            curr_reserved = max(0.0, float(donation.get("quantity_reserved", 0)) - qty)
            curr_distributed = float(donation.get("quantity_distributed", 0))
            published = float(donation.get("quantity_published", 0))
            new_available = max(0.0, published - curr_reserved - curr_distributed)

            new_status = "available" if new_available > 0 else donation.get("status")
            storage.update(Config.DONATIONS_FILE, donation["id"], {
                "quantity_reserved": curr_reserved,
                "quantity_available": new_available,
                "status": new_status
            })

            # Notify donor
            NotificationService.send_notification(
                user_id=donation["donor_id"],
                title="Charity Request Cancelled",
                message=f"{req['organization_name']} cancelled their request for {qty} {donation['unit']} of '{donation['food_name']}'. Quantity released.",
                notif_type="info"
            )

        AuditService.log_event(
            action="CANCEL_REQUEST",
            resource_type="request",
            resource_id=request_id,
            details=f"Cancelled request: {reason}"
        )
        return True, "Request cancelled successfully."
