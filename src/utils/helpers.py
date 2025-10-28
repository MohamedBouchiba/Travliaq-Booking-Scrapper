from datetime import datetime, date

def format_date_booking(d: date) -> str:
    """Formate une date pour l'URL Booking."""
    return d.strftime("%Y-%m-%d")

def parse_booking_date(date_str: str) -> date:
    """Parse une date depuis le format Booking."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()
