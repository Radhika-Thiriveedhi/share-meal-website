from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.request_service import RequestService
from services.donation_service import DonationService
from storage.json_storage import storage
from config import Config
from utils.decorators import login_required, role_required, verified_required

org_bp = Blueprint('org', __name__, url_prefix='/org')

@org_bp.route('/dashboard')
@login_required
@role_required('organization')
@verified_required
def dashboard():
    """Organization dashboard showing incoming food opportunities and active requests."""
    org_id = session.get('user_id')
    my_requests = RequestService.get_organization_requests(org_id)
    
    # Calculate organization statistics
    total_received = sum(float(r.get('quantity_requested', 0)) for r in my_requests if r.get('status') == 'receipt_confirmed')
    active_requests = [r for r in my_requests if r.get('status') in ['pending', 'approved', 'volunteer_assigned', 'picked_up', 'delivered']]
    
    # Available donations showcase
    DonationService.sweep_expired_donations()
    available_donations = storage.find_where(Config.DONATIONS_FILE, lambda d: d.get('status') in ['available', 'request_received', 'partially_fulfilled'] and float(d.get('quantity_available', 0)) > 0)
    
    return render_template(
        'org/dashboard.html',
        active_page='dashboard',
        my_requests=my_requests[:5],
        active_requests_count=len(active_requests),
        total_received=total_received,
        available_donations=available_donations[:4],
        total_available_listings=len(available_donations)
    )

@org_bp.route('/browse')
@login_required
@role_required('organization')
@verified_required
def browse():
    """Browse and filter available surplus food listings."""
    DonationService.sweep_expired_donations()
    
    category = request.args.get('category', '')
    storage_cond = request.args.get('storage_conditions', '')
    query = request.args.get('q', '').strip().lower()

    donations = storage.find_where(
        Config.DONATIONS_FILE,
        lambda d: d.get('status') in ['available', 'request_received', 'partially_fulfilled'] and float(d.get('quantity_available', 0)) > 0
    )

    if category:
        donations = [d for d in donations if d.get('food_category') == category]
    if storage_cond:
        donations = [d for d in donations if d.get('storage_conditions') == storage_cond]
    if query:
        donations = [d for d in donations if query in d.get('food_name', '').lower() or query in d.get('donor_name', '').lower()]

    return render_template(
        'org/browse.html',
        active_page='browse',
        donations=donations,
        categories=Config.FOOD_CATEGORIES,
        storage_conditions=Config.STORAGE_CONDITIONS,
        selected_category=category,
        selected_storage=storage_cond,
        search_query=query
    )

@org_bp.route('/donations/<donation_id>', methods=['GET', 'POST'])
@login_required
@role_required('organization')
@verified_required
def donation_detail(donation_id):
    """View donation safety details and submit food portion request."""
    donation = DonationService.get_donation_by_id(donation_id)
    if not donation:
        flash("Food donation not found or has expired.", "danger")
        return redirect(url_for('org.browse'))

    if request.method == 'POST':
        org_id = session.get('user_id')
        qty = request.form.get('quantity_requested')
        urgency = request.form.get('urgency', 'normal')
        beneficiaries = request.form.get('intended_beneficiaries', '')

        success, message, req = RequestService.create_request(
            organization_id=org_id,
            donation_id=donation_id,
            quantity_requested=qty,
            urgency=urgency,
            intended_beneficiaries=beneficiaries
        )
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for('org.request_detail', request_id=req['id']))

    return render_template('org/donation_detail.html', active_page='browse', donation=donation)

@org_bp.route('/requests')
@login_required
@role_required('organization')
@verified_required
def requests_list():
    """List of all requests made by the receiving organization."""
    org_id = session.get('user_id')
    status_filter = request.args.get('status', 'all')
    
    requests = RequestService.get_organization_requests(org_id)
    if status_filter != 'all':
        requests = [r for r in requests if r.get('status') == status_filter]

    return render_template(
        'org/requests_list.html',
        active_page='requests',
        requests=requests,
        status_filter=status_filter
    )

@org_bp.route('/requests/<request_id>')
@login_required
@role_required('organization')
@verified_required
def request_detail(request_id):
    """View detailed lifecycle of a specific request, volunteer info, and delivery ETA."""
    org_id = session.get('user_id')
    req = RequestService.get_request_by_id(request_id)
    if not req or req.get('organization_id') != org_id:
        flash("Request not found.", "danger")
        return redirect(url_for('org.requests_list'))

    donation = DonationService.get_donation_by_id(req.get('donation_id'))
    return render_template('org/request_detail.html', active_page='requests', req=req, donation=donation)

@org_bp.route('/requests/<request_id>/cancel', methods=['POST'])
@login_required
@role_required('organization')
@verified_required
def cancel_request(request_id):
    """Cancel an active request."""
    org_id = session.get('user_id')
    reason = request.form.get('reason', 'Cancelled by organization')
    success, msg = RequestService.cancel_request(request_id, org_id, reason)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('org.requests_list'))

@org_bp.route('/history')
@login_required
@role_required('organization')
@verified_required
def history():
    """History of received food donations and beneficiary meal distribution."""
    org_id = session.get('user_id')
    my_requests = RequestService.get_organization_requests(org_id)
    completed_requests = [r for r in my_requests if r.get('status') == 'receipt_confirmed']
    total_received = sum(float(r.get('quantity_requested', 0)) for r in completed_requests)

    return render_template(
        'org/history.html',
        active_page='history',
        completed_requests=completed_requests,
        total_received=total_received
    )
