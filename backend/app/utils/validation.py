from datetime import datetime, timezone


def get_current_utc_time():
    return datetime.now(timezone.utc)

def serialize_row(row):
    return [
        item.isoformat() if isinstance(item, datetime) else item
        for item in row
    ]
