import os
from datetime import timedelta

class Config:
    """Base application configuration for ShareMeal platform."""
    # Core Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sharemeal-dev-secure-key-2026-forest-green')
    
    # Session Security
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # Centralized Storage Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
    
    # JSON Data Files
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    DONATIONS_FILE = os.path.join(DATA_DIR, 'donations.json')
    REQUESTS_FILE = os.path.join(DATA_DIR, 'requests.json')
    SAFETY_REPORTS_FILE = os.path.join(DATA_DIR, 'safety_reports.json')
    NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')
    AUDIT_LOGS_FILE = os.path.join(DATA_DIR, 'audit_logs.json')
    
    # Food Safety Constants
    MAX_COLLECTION_HOURS = 72  # Maximum window before forced expiry
    FOOD_CATEGORIES = [
        ('cooked_meals', 'Cooked & Prepared Meals'),
        ('bakery_bread', 'Bakery & Bread Products'),
        ('fresh_produce', 'Fresh Fruits & Vegetables'),
        ('packaged_groceries', 'Packaged & Canned Groceries'),
        ('dairy_chilled', 'Dairy & Chilled Goods'),
        ('beverages', 'Juices & Beverages'),
        ('other', 'Other Surplus Food')
    ]
    
    STORAGE_CONDITIONS = [
        ('room_temperature', 'Room Temperature / Ambient (Dry Shelf)'),
        ('refrigerated', 'Refrigerated (0°C to 4°C / 32°F to 40°F)'),
        ('frozen', 'Frozen (-18°C or below / 0°F)'),
        ('hot_held', 'Hot Held (60°C or above / 140°F)')
    ]
    
    PACKAGING_CONDITIONS = [
        ('sealed_commercial', 'Sealed Commercial Manufacturer Packaging'),
        ('food_grade_containers', 'Food-Grade Sealed Containers / Pans'),
        ('insulated_boxes', 'Insulated Thermal Boxes / Coolers'),
        ('individually_wrapped', 'Individually Wrapped & Labeled Portions')
    ]
    
    COMMON_ALLERGENS = [
        'Gluten (Wheat, Barley, Rye)',
        'Dairy & Lactose',
        'Tree Nuts',
        'Peanuts',
        'Soy & Soybeans',
        'Eggs',
        'Fish',
        'Shellfish & Crustaceans',
        'Sesame',
        'None declared / allergen-free'
    ]
    
    # User Roles
    ROLES = {
        'donor': 'Food Donor',
        'organization': 'Receiving Organization',
        'volunteer': 'Community Volunteer',
        'admin': 'Platform Administrator'
    }
    
    # Donor Sub-types
    DONOR_TYPES = {
        'restaurant': 'Restaurant / Dining Establishment',
        'hotel': 'Hotel / Hospitality Caterer',
        'supermarket': 'Supermarket / Grocery Retailer',
        'bakery': 'Bakery / Patisserie',
        'event_organizer': 'Event Organizer / Banquet Hall'
    }
    
    # Receiving Organization Sub-types
    ORG_TYPES = {
        'ngo': 'Non-Governmental Organization (NGO)',
        'shelter': 'Emergency Shelter / Transitional Housing',
        'community_kitchen': 'Community Kitchen / Soup Kitchen'
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    DATA_DIR = os.path.join(Config.BASE_DIR, 'tests', 'test_data')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    DONATIONS_FILE = os.path.join(DATA_DIR, 'donations.json')
    REQUESTS_FILE = os.path.join(DATA_DIR, 'requests.json')
    SAFETY_REPORTS_FILE = os.path.join(DATA_DIR, 'safety_reports.json')
    NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')
    AUDIT_LOGS_FILE = os.path.join(DATA_DIR, 'audit_logs.json')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
