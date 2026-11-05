from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.volunteer_service import VolunteerService
from services.donation_service import DonationService
from services.request_service import RequestService
from services.safety_service import SafetyService
from storage.json_storage import storage
from config import Config
from utils.decorators import login_required, role_required, verified_required

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

@volunteer_bp.route('/dashboard')
@login_required
@role_required('volunteer')
@verified_required
def dashboard():
    """Volunteer operations center: active mission, available dispatches, and lifetime stats."""
    volunteer_id = session.get('user_id')
    my_missions = VolunteerService.get_volunteer_missions(volunteer_id)
    
    active_mission = next((m for m in my_missions if m.get('status') in ['volunteer_assigned', 'picked_up']), None)
    active_donation = DonationService.get_donation_by_id(active_mission.get('donation_id')) if active_mission else None

    available_tasks = VolunteerService.get_available_tasks()
    completed_missions = [m for m in my_missions if m.get('status') in ['delivered', 'receipt_confirmed']]
    
    return render_template(
        'volunteer/dashboard.html',
        active_page='dashboard',
        active_mission=active_mission,
        active_donation=active_donation,
        available_tasks_count=len(available_tasks),
        completed_count=len(completed_missions),
        available_preview=available_tasks[:3]
    )

@volunteer_bp.route('/tasks')
@login_required
@role_required('volunteer')
@verified_required
def tasks_available():
    """List of approved food collections needing courier transport."""
    tasks = VolunteerService.get_available_tasks()
    return render_template('volunteer/tasks_available.html', active_page='available_tasks', tasks=tasks)

@volunteer_bp.route('/tasks/<request_id>/accept', methods=['POST'])
@login_required
@role_required('volunteer')
@verified_required
def accept_task(request_id):
    """Claim a collection mission."""
    volunteer_id = session.get('user_id')
    success, msg = VolunteerService.accept_task(request_id, volunteer_id)
    flash(msg, "success" if success else "danger")
    if success:
        return redirect(url_for('volunteer.task_detail', request_id=request_id))
    return redirect(url_for('volunteer.tasks_available'))

@volunteer_bp.route('/tasks/<request_id>')
@login_required
@role_required('volunteer')
@verified_required
def task_detail(request_id):
    """Mission dispatch sheet: pickup address, donor phone, receiver instructions."""
    volunteer_id = session.get('user_id')
    req = RequestService.get_request_by_id(request_id)
    if not req or req.get('volunteer_id') != volunteer_id:
        flash("Unauthorized or mission not found.", "danger")
        return redirect(url_for('volunteer.dashboard'))

    donation = DonationService.get_donation_by_id(req.get('donation_id'))
    receiver = storage.find_by_id(Config.USERS_FILE, req.get('organization_id'))

    return render_template(
        'volunteer/task_detail.html',
        active_page='dashboard',
        req=req,
        donation=donation,
        receiver=receiver
    )

@volunteer_bp.route('/tasks/<request_id>/pickup', methods=['GET', 'POST'])
@login_required
@role_required('volunteer')
@verified_required
def pickup_confirm(request_id):
    """Volunteer physical pickup verification checklist."""
    volunteer_id = session.get('user_id')
    req = RequestService.get_request_by_id(request_id)
    if not req or req.get('volunteer_id') != volunteer_id:
        flash("Mission not found.", "danger")
        return redirect(url_for('volunteer.dashboard'))

    donation = DonationService.get_donation_by_id(req.get('donation_id'))

    if request.method == 'POST':
        notes = request.form.get('pickup_notes', '')
        success, msg = VolunteerService.confirm_pickup(request_id, volunteer_id, notes)
        flash(msg, "success" if success else "danger")
        return redirect(url_for('volunteer.task_detail', request_id=request_id))

    return render_template('volunteer/pickup_confirm.html', req=req, donation=donation)

@volunteer_bp.route('/tasks/<request_id>/deliver', methods=['GET', 'POST'])
@login_required
@role_required('volunteer')
@verified_required
def delivery_confirm(request_id):
    """Volunteer delivery completion at charity facility."""
    volunteer_id = session.get('user_id')
    req = RequestService.get_request_by_id(request_id)
    if not req or req.get('volunteer_id') != volunteer_id:
        flash("Mission not found.", "danger")
        return redirect(url_for('volunteer.dashboard'))

    donation = DonationService.get_donation_by_id(req.get('donation_id'))
    receiver = storage.find_by_id(Config.USERS_FILE, req.get('organization_id'))

    if request.method == 'POST':
        notes = request.form.get('delivery_notes', '')
        success, msg = VolunteerService.confirm_delivery(request_id, volunteer_id, notes)
        flash(msg, "success" if success else "danger")
        return redirect(url_for('volunteer.history'))

    return render_template('volunteer/delivery_confirm.html', req=req, donation=donation, receiver=receiver)

@volunteer_bp.route('/tasks/<request_id>/report-issue', methods=['GET', 'POST'])
@login_required
@role_required('volunteer')
@verified_required
def report_issue(request_id):
    """Volunteer reports collection delays, temperature violations, or packaging defects."""
    volunteer_id = session.get('user_id')
    req = RequestService.get_request_by_id(request_id)
    if not req or req.get('volunteer_id') != volunteer_id:
        flash("Mission not found.", "danger")
        return redirect(url_for('volunteer.dashboard'))

    donation = DonationService.get_donation_by_id(req.get('donation_id'))

    if request.method == 'POST':
        issue_type = request.form.get('issue_type')
        description = request.form.get('description', '')

        SafetyService.file_report(
            donation_id=donation['id'],
            reporter_id=volunteer_id,
            reporter_role='volunteer',
            reporter_name=session.get('name'),
            report_type=issue_type,
            description=description,
            request_id=request_id
        )
        flash("Safety incident reported. The food item has been quarantined for admin review.", "warning")
        return redirect(url_for('volunteer.dashboard'))

    return render_template('volunteer/report_issue.html', req=req, donation=donation)

@volunteer_bp.route('/history')
@login_required
@role_required('volunteer')
@verified_required
def history():
    """Completed mission history and community service record."""
    volunteer_id = session.get('user_id')
    my_missions = VolunteerService.get_volunteer_missions(volunteer_id)
    completed = [m for m in my_missions if m.get('status') in ['delivered', 'receipt_confirmed']]
    
    return render_template(
        'volunteer/history.html',
        active_page='history',
        completed_missions=completed
    )
