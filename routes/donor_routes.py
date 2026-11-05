from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.donation_service import DonationService
from storage.json_storage import storage
from config import Config
from utils.decorators import login_required, role_required, verified_required

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

@donor_bp.route('/dashboard')
@login_required
@role_required('donor')
@verified_required
def dashboard():
    """Donor overview with inventory stats, active listings, and incoming requests."""
    donor_id = session.get('user_id')
    donations = DonationService.get_donor_donations(donor_id)
    
    # Calculate real donor metrics
    total_published = sum(float(d.get('quantity_published', 0)) for d in donations)
    total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in donations)
    active_listings = [d for d in donations if d.get('status') in ['available', 'request_received', 'confirmed', 'partially_fulfilled']]
    
    # Find all requests for this donor's listings
    donation_ids = {d['id'] for d in donations}
    all_requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get('donation_id') in donation_ids)
    pending_requests = [r for r in all_requests if r.get('status') == 'pending']
    
    return render_template(
        'donor/dashboard.html',
        active_page='dashboard',
        donations=donations[:5],
        active_listings_count=len(active_listings),
        pending_requests_count=len(pending_requests),
        total_published=total_published,
        total_distributed=total_distributed,
        pending_requests=pending_requests[:5]
    )

@donor_bp.route('/donations/create', methods=['GET', 'POST'])
@login_required
@role_required('donor')
@verified_required
def create_donation():
    """Form to publish a surplus food donation with safety parameters."""
    if request.method == 'POST':
        donor_id = session.get('user_id')
        allergens = request.form.getlist('allergens')
        data = {
            'food_name': request.form.get('food_name'),
            'food_category': request.form.get('food_category'),
            'quantity_published': request.form.get('quantity_published'),
            'unit': request.form.get('unit'),
            'preparation_datetime': request.form.get('preparation_datetime'),
            'collection_deadline': request.form.get('collection_deadline'),
            'storage_conditions': request.form.get('storage_conditions'),
            'allergens': allergens,
            'packaging_condition': request.form.get('packaging_condition'),
            'pickup_address': request.form.get('pickup_address'),
            'pickup_instructions': request.form.get('pickup_instructions', ''),
            'special_handling_notes': request.form.get('special_handling_notes', '')
        }

        success, message, donation = DonationService.create_donation(donor_id, data)
        if success:
            flash(message, "success")
            return redirect(url_for('donor.donations_list'))
        else:
            if isinstance(message, dict):
                for field, err in message.items():
                    flash(f"{field.replace('_', ' ').capitalize()}: {err}", "danger")
            else:
                flash(message, "danger")

    return render_template(
        'donor/create_donation.html',
        active_page='create_donation',
        categories=Config.FOOD_CATEGORIES,
        storage_conditions=Config.STORAGE_CONDITIONS,
        packaging_conditions=Config.PACKAGING_CONDITIONS,
        common_allergens=Config.COMMON_ALLERGENS
    )

@donor_bp.route('/donations')
@login_required
@role_required('donor')
@verified_required
def donations_list():
    """Manage table of all donor listings with status filters."""
    donor_id = session.get('user_id')
    status_filter = request.args.get('status', 'all')
    
    donations = DonationService.get_donor_donations(donor_id)
    if status_filter != 'all':
        donations = [d for d in donations if d.get('status') == status_filter]
        
    return render_template(
        'donor/donations_list.html',
        active_page='donations',
        donations=donations,
        status_filter=status_filter
    )

@donor_bp.route('/donations/<donation_id>')
@login_required
@role_required('donor')
@verified_required
def donation_detail(donation_id):
    """Deep dive into a specific donation listing and associated requests."""
    donor_id = session.get('user_id')
    donation = DonationService.get_donation_by_id(donation_id)
    if not donation or donation.get('donor_id') != donor_id:
        flash("Donation not found.", "danger")
        return redirect(url_for('donor.donations_list'))

    requests = storage.find_where(Config.REQUESTS_FILE, lambda r: r.get('donation_id') == donation_id)
    return render_template('donor/donation_detail.html', active_page='donations', donation=donation, requests=requests)

@donor_bp.route('/donations/<donation_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('donor')
@verified_required
def edit_donation(donation_id):
    """Edit unreserved donation details."""
    donor_id = session.get('user_id')
    donation = DonationService.get_donation_by_id(donation_id)
    if not donation or donation.get('donor_id') != donor_id:
        flash("Donation not found.", "danger")
        return redirect(url_for('donor.donations_list'))

    if request.method == 'POST':
        allergens = request.form.getlist('allergens')
        updates = {
            'food_name': request.form.get('food_name'),
            'food_category': request.form.get('food_category'),
            'quantity_published': request.form.get('quantity_published'),
            'unit': request.form.get('unit'),
            'preparation_datetime': request.form.get('preparation_datetime'),
            'collection_deadline': request.form.get('collection_deadline'),
            'storage_conditions': request.form.get('storage_conditions'),
            'allergens': allergens,
            'packaging_condition': request.form.get('packaging_condition'),
            'pickup_address': request.form.get('pickup_address'),
            'pickup_instructions': request.form.get('pickup_instructions', ''),
            'special_handling_notes': request.form.get('special_handling_notes', '')
        }
        success, msg = DonationService.update_donation(donation_id, donor_id, updates)
        flash(msg, "success" if success else "danger")
        if success:
            return redirect(url_for('donor.donation_detail', donation_id=donation_id))

    return render_template(
        'donor/edit_donation.html',
        active_page='donations',
        donation=donation,
        categories=Config.FOOD_CATEGORIES,
        storage_conditions=Config.STORAGE_CONDITIONS,
        packaging_conditions=Config.PACKAGING_CONDITIONS,
        common_allergens=Config.COMMON_ALLERGENS
    )

@donor_bp.route('/donations/<donation_id>/cancel', methods=['POST'])
@login_required
@role_required('donor')
@verified_required
def cancel_donation(donation_id):
    """Cancel an active donation."""
    donor_id = session.get('user_id')
    reason = request.form.get('reason', 'Cancelled by donor')
    success, msg = DonationService.cancel_donation(donation_id, donor_id, reason)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('donor.donations_list'))

@donor_bp.route('/history')
@login_required
@role_required('donor')
@verified_required
def history():
    """Historical completed donations and social impact summaries."""
    donor_id = session.get('user_id')
    donations = DonationService.get_donor_donations(donor_id)
    completed_donations = [d for d in donations if d.get('status') == 'completed']
    total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in completed_donations)
    
    return render_template(
        'donor/history.html',
        active_page='history',
        completed_donations=completed_donations,
        total_distributed=total_distributed
    )
