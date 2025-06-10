from datetime import datetime, timezone
from app.db.connection import cursor

def get_current_utc_time():
    return datetime.now(timezone.utc)

def serialize_row(row):
    column_names = [desc[0] for desc in cursor.description]
    return {
        column: (value.isoformat() if isinstance(value, datetime) else value)
        for column, value in zip(column_names, row)
    }
