from sqlalchemy import BigInteger, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from typing import Optional

class User(Base):
    __tablename__="users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone_no: Mapped[Optional[int]] = mapped_column(BigInteger,)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, onupdate=func.now(), server_default=func.now())
    

