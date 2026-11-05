from storage.json_storage import storage
from config import Config
from collections import defaultdict

class AnalyticsService:
    @staticmethod
    def get_summary_metrics():
        """
        Compute high-level verified platform metrics directly from stored records:
        - total donations published
        - total food quantity distributed
        - total food currently reserved
        - total food currently available
        - completed collection count
        - active volunteer count
        - expired and cancelled donation count
        """
        donations = storage.find_all(Config.DONATIONS_FILE)
        requests = storage.find_all(Config.REQUESTS_FILE)
        users = storage.find_all(Config.USERS_FILE)

        total_published = sum(float(d.get('quantity_published', 0)) for d in donations)
        total_reserved = sum(float(d.get('quantity_reserved', 0)) for d in donations)
        total_distributed = sum(float(d.get('quantity_distributed', 0)) for d in donations)
        total_available = sum(float(d.get('quantity_available', 0)) for d in donations)

        completed_requests = len([r for r in requests if r.get('status') == 'receipt_confirmed'])
        pending_requests = len([r for r in requests if r.get('status') == 'pending'])
        active_volunteers = len([u for u in users if u.get('role') == 'volunteer' and u.get('verification_status') == 'verified' and u.get('is_active', True)])
        
        expired_count = len([d for d in donations if d.get('status') == 'expired'])
        cancelled_count = len([d for d in donations if d.get('status') == 'cancelled'])

        # Environmental impacts
        co2_saved = round(total_distributed * 2.5, 1)
        water_saved = round(total_distributed * 450, 0)

        return {
            'total_published': total_published,
            'total_reserved': total_reserved,
            'total_distributed': total_distributed,
            'total_available': total_available,
            'completed_collections': completed_requests,
            'pending_requests': pending_requests,
            'active_volunteers': active_volunteers,
            'expired_count': expired_count,
            'cancelled_count': cancelled_count,
            'co2_saved_kg': co2_saved,
            'water_saved_liters': water_saved
        }

    @staticmethod
    def get_category_breakdown():
        """Calculate food volume distributed by category."""
        donations = storage.find_all(Config.DONATIONS_FILE)
        cat_map = defaultdict(float)
        for d in donations:
            cat = d.get('food_category', 'other')
            qty = float(d.get('quantity_published', 0))
            cat_map[cat] += qty

        colors = ['#2D5A27', '#4E7D47', '#739F6B', '#D97706', '#E07A5F', '#5F6C64', '#9BB896']
        items = []
        for idx, (cat_key, cat_label) in enumerate(Config.FOOD_CATEGORIES):
            val = round(cat_map.get(cat_key, 0.0), 1)
            items.append({
                'label': cat_label.split('&')[0].strip(),
                'value': val,
                'color': colors[idx % len(colors)]
            })
        return items

    @staticmethod
    def get_donor_leaderboard(limit=5):
        """Top contributing food donors by total published and distributed surplus."""
        donations = storage.find_all(Config.DONATIONS_FILE)
        donor_stats = defaultdict(lambda: {'name': '', 'published': 0.0, 'distributed': 0.0, 'listings': 0})

        for d in donations:
            donor_id = d.get('donor_id')
            donor_stats[donor_id]['name'] = d.get('donor_name', 'Anonymous Kitchen')
            donor_stats[donor_id]['published'] += float(d.get('quantity_published', 0))
            donor_stats[donor_id]['distributed'] += float(d.get('quantity_distributed', 0))
            donor_stats[donor_id]['listings'] += 1

        leaderboard = list(donor_stats.values())
        leaderboard.sort(key=lambda x: x['distributed'], reverse=True)
        return leaderboard[:limit]

    @staticmethod
    def get_organization_leaderboard(limit=5):
        """Top receiving charitable organizations by verified food received."""
        requests = storage.find_all(Config.REQUESTS_FILE)
        org_stats = defaultdict(lambda: {'name': '', 'received': 0.0, 'completed': 0})

        for r in requests:
            if r.get('status') == 'receipt_confirmed':
                org_id = r.get('organization_id')
                org_stats[org_id]['name'] = r.get('organization_name', 'Charity')
                org_stats[org_id]['received'] += float(r.get('quantity_requested', 0))
                org_stats[org_id]['completed'] += 1

        leaderboard = list(org_stats.values())
        leaderboard.sort(key=lambda x: x['received'], reverse=True)
        return leaderboard[:limit]
