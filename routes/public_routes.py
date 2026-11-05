from flask import Blueprint, render_template, request, flash, redirect, url_for
from storage.json_storage import storage
from config import Config
from services.audit_service import AuditService

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Public home page with real stored metrics and active community listings."""
    donations = storage.find_all(Config.DONATIONS_FILE)
    users = storage.find_all(Config.USERS_FILE)
    
    # Calculate live real metrics directly from stored records
    total_published = sum(float(d.get('quantity_published', 0)) for d in donations)
    total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in donations)
    active_donations_count = len([d for d in donations if d.get('status') == 'available'])
    active_partners_count = len([u for u in users if u.get('verification_status') == 'verified'])
    
    # Showcase up to 4 available donations
    available_showcase = [d for d in donations if d.get('status') == 'available'][:4]
    
    return render_template(
        'public/index.html',
        total_published=total_published,
        total_distributed=total_distributed,
        active_donations_count=active_donations_count,
        active_partners_count=active_partners_count,
        available_showcase=available_showcase
    )

@public_bp.route('/about')
def about():
    """Mission, problem context, and organizational background."""
    return render_template('public/about.html')

@public_bp.route('/how-it-works')
def how_it_works():
    """Step-by-step role lifecycle explainer."""
    return render_template('public/how_it_works.html')

@public_bp.route('/food-safety')
def food_safety():
    """Platform food safety guidelines, temperature rules, and legal compliance."""
    return render_template('public/food_safety.html')

@public_bp.route('/impact')
def impact():
    """Detailed live community distribution and sustainability metrics."""
    donations = storage.find_all(Config.DONATIONS_FILE)
    requests = storage.find_all(Config.REQUESTS_FILE)
    
    total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in donations)
    completed_requests = len([r for r in requests if r.get('status') == 'receipt_confirmed'])
    
    # Environmental metrics formula: ~2.5 kg CO2e saved per kg food rescued, 450L water per kg
    co2_saved = round(total_distributed * 2.5, 1)
    water_saved = round(total_distributed * 450, 0)
    
    return render_template(
        'public/impact.html',
        total_distributed=total_distributed,
        completed_requests=completed_requests,
        co2_saved=co2_saved,
        water_saved=water_saved
    )

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page and message receiver."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if name and email and message:
            AuditService.log_event(
                action="CONTACT_FORM_SUBMISSION",
                resource_type="contact",
                details=f"Message from {name} ({email})"
            )
            flash("Thank you for reaching out! Our community coordinator will respond within 24 hours.", "success")
            return redirect(url_for('public.contact'))
        else:
            flash("Please fill out all required contact fields.", "warning")
            
    return render_template('public/contact.html')

@public_bp.route('/terms')
def terms():
    """Terms of service and Good Samaritan liability shield documentation."""
    return render_template('public/terms.html')
