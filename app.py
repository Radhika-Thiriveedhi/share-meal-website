import os
from flask import Flask, render_template, session
from config import Config
from storage.json_storage import storage
from storage.seed_data import seed_database
from services.notification_service import NotificationService
from utils.security import generate_csrf_token
from utils.date_helpers import parse_iso, format_datetime, format_date, time_remaining_human

# Import Blueprints
from routes.public_routes import public_bp
from routes.auth_routes import auth_bp
from routes.donor_routes import donor_bp
from routes.org_routes import org_bp
from routes.volunteer_routes import volunteer_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp

def create_app(config_class=Config):
    """
    Application factory pattern for ShareMeal platform.
    Initializes storage, context processors, custom filters, and registers blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure persistence directories exist
    os.makedirs(app.config.get('DATA_DIR', 'data'), exist_ok=True)
    os.makedirs(app.config.get('BACKUP_DIR', os.path.join(app.config.get('DATA_DIR', 'data'), 'backups')), exist_ok=True)

    # Populate realistic seed dataset if not populated
    try:
        seed_database(force=False)
    except Exception as e:
        app.logger.warning(f"Seed data check note: {e}")

    # Register Role & Feature Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(volunteer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    # Global Context Processors
    @app.context_processor
    def inject_platform_context():
        unread_count = 0
        user_id = session.get('user_id')
        if user_id:
            try:
                unread_count = NotificationService.get_unread_count(user_id)
            except Exception:
                unread_count = 0

        return {
            'csrf_token': generate_csrf_token,
            'unread_notifications_count': unread_count,
            'current_user_id': user_id,
            'current_user_role': session.get('role'),
            'current_user_name': session.get('name'),
            'current_user_email': session.get('email'),
            'app_name': 'ShareMeal',
            'support_email': 'support@sharemeal.org'
        }

    # Template Formatting Filters
    @app.template_filter('format_datetime')
    def filter_format_datetime(value, fmt="%b %d, %Y %I:%M %p"):
        return format_datetime(value, fmt)

    @app.template_filter('format_date')
    def filter_format_date(value):
        return format_date(value)

    @app.template_filter('time_remaining')
    def filter_time_remaining(value):
        return time_remaining_human(value)

    # Humanized Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
