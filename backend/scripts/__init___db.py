# backend/scripts/init_db.py

import asyncio
from app.db import initialize_db

if __name__ == "__main__":
    asyncio.run(initialize_db())
