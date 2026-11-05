from datetime import datetime
from storage.json_storage import storage
from services.audit_service import AuditService
from services.notification_service import NotificationService
from services.donation_service import DonationService
from config import Config

class VolunteerService:
    @staticmethod
    def get_available_tasks():
        """
        Find approved food requests that need a volunteer courier
        (i.e. status is 'approved' and volunteer_id is None).
        """
        DonationService.sweep_expired_donations()
        
        # Get all approved requests
        requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get("status") == "approved" and not r.get("volunteer_id"))
        
        # Hydrate with donation details
        tasks = []
        for req in requests:
            don = storage.find_by_id(Config.DONATIONS_FILE, req.get("donation_id"))
            if don and don.get("status") in ["confirmed", "partially_fulfilled"]:
                task_data = dict(req)
                task_data["food_name"] = don.get("food_name")
                task_data["food_category"] = don.get("food_category")
                task_data["unit"] = don.get("unit")
                task_data["storage_conditions"] = don.get("storage_conditions")
                task_data["packaging_condition"] = don.get("packaging_condition")
                task_data["pickup_address"] = don.get("pickup_address")
                task_data["pickup_instructions"] = don.get("pickup_instructions")
                task_data["collection_deadline"] = don.get("collection_deadline")
                task_data["donor_name"] = don.get("donor_name")
                task_data["donor_phone"] = don.get("donor_phone")
                tasks.append(task_data)
        return tasks

    @staticmethod
    def accept_task(request_id, volunteer_id):
        """Volunteer accepts collection dispatch mission."""
        req = storage.find_by_id(Config.REQUESTS_FILE, request_id)
        if not req or req.get("status") != "approved" or req.get("volunteer_id"):
            return False, "This mission has already been claimed or is no longer available."

        vol = storage.find_by_id(Config.USERS_FILE, volunteer_id)
        if not vol or vol.get("role") != "volunteer":
            return False, "Unauthorized volunteer account."

        # Assign volunteer to request
        storage.update(Config.REQUESTS_FILE, request_id, {
            "status": "volunteer_assigned",
            "volunteer_id": volunteer_id,
            "volunteer_name": vol.get("name"),
            "volunteer_phone": vol.get("phone", "")
        })

        # Update donation status
        storage.update(Config.DONATIONS_FILE, req.get("donation_id"), {
            "status": "volunteer_assigned"
        })

        AuditService.log_event(
            action="VOLUNTEER_ACCEPT_TASK",
            resource_type="request",
            resource_id=request_id,
            details=f"Volunteer {vol['name']} accepted collection mission"
        )

        # Notify donor and organization
        donation = storage.find_by_id(Config.DONATIONS_FILE, req.get("donation_id"))
        NotificationService.send_notification(
            user_id=donation["donor_id"],
            title="Volunteer Courier Dispatched",
            message=f"Volunteer {vol['name']} is en route to collect '{donation['food_name']}'.",
            notif_type="info",
            link="/donor/requests"
        )

        NotificationService.send_notification(
            user_id=req["organization_id"],
            title="Volunteer Assigned to Your Delivery",
            message=f"Volunteer {vol['name']} has claimed your food delivery.",
            notif_type="info",
            link=f"/org/requests/{request_id}"
        )

        return True, "Mission accepted. Donor pickup details are now unlocked."

    @staticmethod
    def confirm_pickup(request_id, volunteer_id, pickup_notes=""):
        """Volunteer verifies pickup from donor kitchen."""
        req = storage.find_by_id(Config.REQUESTS_FILE, request_id)
        if not req or req.get("volunteer_id") != volunteer_id or req.get("status") != "volunteer_assigned":
            return False, "Unauthorized or task not in assigned state."

        now = datetime.utcnow().isoformat()
        storage.update(Config.REQUESTS_FILE, request_id, {
            "status": "picked_up",
            "pickup_time": now,
            "pickup_notes": pickup_notes.strip()
        })

        storage.update(Config.DONATIONS_FILE, req.get("donation_id"), {
            "status": "picked_up"
        })

        AuditService.log_event(
            action="CONFIRM_PICKUP",
            resource_type="request",
            resource_id=request_id,
            details=f"Pickup verified by volunteer. Notes: {pickup_notes}"
        )

        donation = storage.find_by_id(Config.DONATIONS_FILE, req.get("donation_id"))
        NotificationService.send_notification(
            user_id=req["organization_id"],
            title="Food Picked Up — En Route to You",
            message=f"Courier {req['volunteer_name']} has picked up {req['quantity_requested']} {donation.get('unit', '')} of '{donation['food_name']}'.",
            notif_type="info",
            link=f"/org/requests/{request_id}"
        )

        return True, "Pickup confirmed. Please proceed to the charity delivery facility."

    @staticmethod
    def confirm_delivery(request_id, volunteer_id, delivery_notes=""):
        """Volunteer confirms arrival and handoff at charity shelter."""
        req = storage.find_by_id(Config.REQUESTS_FILE, request_id)
        if not req or req.get("volunteer_id") != volunteer_id or req.get("status") != "picked_up":
            return False, "Unauthorized or task not in picked up state."

        now = datetime.utcnow().isoformat()
        storage.update(Config.REQUESTS_FILE, request_id, {
            "status": "delivered",
            "delivered_time": now,
            "delivery_notes": delivery_notes.strip()
        })

        storage.update(Config.DONATIONS_FILE, req.get("donation_id"), {
            "status": "delivered"
        })

        AuditService.log_event(
            action="CONFIRM_DELIVERY",
            resource_type="request",
            resource_id=request_id,
            details=f"Food delivered to charity facility. Notes: {delivery_notes}"
        )

        # Notify organization supervisor to sign off
        donation = storage.find_by_id(Config.DONATIONS_FILE, req.get("donation_id"))
        NotificationService.send_notification(
            user_id=req["organization_id"],
            title="Food Delivered — Confirmation Sign-off Required",
            message=f"Courier {req['volunteer_name']} delivered '{donation['food_name']}'. Please inspect and confirm receipt.",
            notif_type="warning",
            link=f"/org/requests/{request_id}"
        )

        return True, "Delivery recorded. The charity facility supervisor will inspect and confirm receipt."

    @staticmethod
    def get_volunteer_missions(volunteer_id):
        """Get active and completed tasks for a volunteer."""
        requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get("volunteer_id") == volunteer_id)
        requests.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return requests
