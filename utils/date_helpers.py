from datetime import datetime, timezone

def parse_iso(dt_string):
    """Safely parse ISO datetime string into a naive UTC datetime object."""
    if not dt_string:
        return None
    try:
        cleaned = dt_string.replace("Z", "").split("+")[0]
        if "T" in cleaned:
            return datetime.fromisoformat(cleaned)
        return datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(dt_string, "%Y-%m-%d")
        except Exception:
            return None

def format_datetime(dt_string, fmt="%b %d, %Y %I:%M %p"):
    """Format an ISO string to a human-readable representation."""
    dt = parse_iso(dt_string)
    if not dt:
        return "N/A"
    return dt.strftime(fmt)

def format_date(dt_string):
    """Format an ISO string to a clean date."""
    return format_datetime(dt_string, fmt="%b %d, %Y")

def is_expired(deadline_str):
    """Check if the given collection deadline has passed."""
    deadline = parse_iso(deadline_str)
    if not deadline:
        return True
    return datetime.utcnow() > deadline

def time_remaining_human(deadline_str):
    """Return a human-friendly countdown string for collection deadlines."""
    deadline = parse_iso(deadline_str)
    if not deadline:
        return "Expired"
    now = datetime.utcnow()
    diff = deadline - now
    if diff.total_seconds() <= 0:
        return "Expired"
    hours, remainder = divmod(int(diff.total_seconds()), 3600)
    minutes = remainder // 60
    if hours >= 24:
        days = hours // 24
        return f"{days}d {hours % 24}h remaining"
    if hours > 0:
        return f"{hours}h {minutes}m remaining"
    return f"{minutes}m remaining"
