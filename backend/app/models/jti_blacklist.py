from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base

class JTIBlacklist(Base):
    __tablename__="jti_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(255), nullable=False, unique=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=True)