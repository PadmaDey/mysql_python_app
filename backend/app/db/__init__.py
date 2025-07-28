from app.models.user import User
from app.models.jti_blacklist import JTIBlacklist
from app.db.database import Base, engine

async def initialize_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    