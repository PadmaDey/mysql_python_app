from sqlalchemy import Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class JTIBlacklist(Base):
    __tablename__="jti_blacklist"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())

