from datetime import datetime
from storage.json_storage import storage
from storage.models import SafetyReportModel
from services.audit_service import AuditService
from services.notification_service import NotificationService
from config import Config

class SafetyService:
    @staticmethod
    def file_report(donation_id, reporter_id, reporter_role, reporter_name,
                    report_type, description, incident_time="", request_id=None):
        """
        File an urgent food safety or quality hazard report.
        Automatically freezes the donation status to 'safety_review'
        to prevent any further collection or distribution until an administrator investigates.
        """
        now = datetime.utcnow().isoformat()
        report = SafetyReportModel.create(
            donation_id=donation_id,
            reporter_id=reporter_id,
            reporter_role=reporter_role,
            reporter_name=reporter_name,
            report_type=report_type,
            description=description,
            incident_time=incident_time or now,
            request_id=request_id
        )
        storage.insert(Config.SAFETY_REPORTS_FILE, report)

        # QUARANTINE: Freeze donation status to safety_review
        donation = storage.find_by_id(Config.DONATIONS_FILE, donation_id)
        if donation:
            storage.update(Config.DONATIONS_FILE, donation_id, {
                "status": "safety_review",
                "safety_review_reason": f"Quarantined: {report_type.replace('_', ' ').capitalize()} - {description[:60]}"
            })

            # Notify donor of quarantine
            NotificationService.send_notification(
                user_id=donation["donor_id"],
                title="URGENT: Listing Quarantined for Safety Review",
                message=f"Your listing for '{donation['food_name']}' has been quarantined due to a reported safety concern ({report_type}). An administrator will review this shortly.",
                notif_type="danger",
                link="/donor/donations"
            )

        # Notify all platform administrators immediately
        NotificationService.notify_admins(
            title="CRITICAL: Food Safety Report Filed",
            message=f"{reporter_name} ({reporter_role}) reported {report_type} for donation {donation_id}. Listing quarantined.",
            notif_type="danger",
            link="/admin/safety-reports"
        )

        AuditService.log_event(
            action="FILE_SAFETY_REPORT",
            resource_type="safety_report",
            resource_id=report["id"],
            details=f"Quarantined donation {donation_id}: {report_type} by {reporter_name} ({reporter_role})"
        )

        return True, "Safety report submitted. The food listing has been quarantined for administrator review.", report

    @staticmethod
    def get_all_reports():
        """Retrieve all safety reports ordered by recency."""
        reports = storage.find_all(Config.SAFETY_REPORTS_FILE)
        reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return reports

    @staticmethod
    def get_report_by_id(report_id):
        """Find safety report by ID."""
        return storage.find_by_id(Config.SAFETY_REPORTS_FILE, report_id)

    @staticmethod
    def resolve_report(report_id, admin_id, resolution, admin_notes=""):
        """
        Administrator resolves a safety investigation.
        Resolution options:
        - 'resolved_safe': Verified safe, restore donation to available (or confirmed).
        - 'resolved_discarded': Hazardous or spoiled; discard permanently, set status to 'cancelled'.
        - 'dismissed': Invalid report.
        """
        report = storage.find_by_id(Config.SAFETY_REPORTS_FILE, report_id)
        if not report or report.get("status") != "under_review":
            return False, "Report not found or already resolved."

        admin = storage.find_by_id(Config.USERS_FILE, admin_id)
        now = datetime.utcnow().isoformat()

        storage.update(Config.SAFETY_REPORTS_FILE, report_id, {
            "status": resolution,
            "resolution": resolution,
            "admin_notes": admin_notes.strip(),
            "reviewed_by": admin.get("name") if admin else "Administrator",
            "reviewed_at": now
        })

        donation = storage.find_by_id(Config.DONATIONS_FILE, report.get("donation_id"))
        if donation:
            if resolution == "resolved_safe":
                # Restore listing
                new_status = "available" if float(donation.get("quantity_available", 0)) > 0 else "confirmed"
                storage.update(Config.DONATIONS_FILE, donation["id"], {
                    "status": new_status,
                    "safety_review_reason": ""
                })
                NotificationService.send_notification(
                    user_id=donation["donor_id"],
                    title="Safety Quarantine Lifted",
                    message=f"Administrator review completed for '{donation['food_name']}'. Listing has been cleared and restored to {new_status}.",
                    notif_type="success",
                    link="/donor/donations"
                )
            elif resolution in ["resolved_discarded", "dismissed"]:
                # Permanently cancel listing and set available to 0
                storage.update(Config.DONATIONS_FILE, donation["id"], {
                    "status": "cancelled",
                    "quantity_available": 0.0,
                    "cancellation_reason": f"Discarded following safety review: {admin_notes}"
                })
                NotificationService.send_notification(
                    user_id=donation["donor_id"],
                    title="Listing Cancelled by Safety Admin",
                    message=f"Listing '{donation['food_name']}' was discarded following investigation. Notes: {admin_notes}",
                    notif_type="danger",
                    link="/donor/donations"
                )

        AuditService.log_event(
            action="RESOLVE_SAFETY_REPORT",
            resource_type="safety_report",
            resource_id=report_id,
            details=f"Admin resolved report as {resolution}. Notes: {admin_notes}"
        )

        return True, f"Safety report resolved as {resolution.replace('_', ' ').capitalize()}."
