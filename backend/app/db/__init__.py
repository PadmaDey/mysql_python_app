from app.models.user import User
from app.models.jti_blacklist import JTIBlacklist
from app.db.database import Base, engine

def initialize_db():
    Base.metadata.create_all(bind=engine)