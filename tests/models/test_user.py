# tests/models/test_user.py

import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from backend.app.db.database import AsyncSessionLocal


@pytest.fixture
def test_email_list():
    """Collects test emails to clean them up later."""
    return []


@pytest.fixture(autouse=True)
async def cleanup_test_users(test_email_list):
    """Cleanup created test users after each test using async-safe logic."""
    yield
    if test_email_list:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(User).where(User.email.in_(test_email_list)))
            await session.commit()


# @pytest.mark.asyncio
# async def test_create_user(db_session, test_email_list):
#     email = "unittestuser@example.com"
#     test_email_list.append(email)

#     user = User(
#         name="Unit User",
#         email=email,
#         phone_no=1234567890,
#         password_hash="hashed_pass"
#     )

#     db_session.add(user)
#     await db_session.commit()

#     result = await db_session.execute(select(User).where(User.email == email))
#     saved_user = result.scalar_one_or_none()

#     assert saved_user is not None
#     assert saved_user.name == "Unit User"
#     assert saved_user.phone_no == 1234567890
#     assert saved_user.password_hash == "hashed_pass"
#     assert saved_user.created_at is not None
#     assert saved_user.updated_at is not None


# @pytest.mark.asyncio
# async def test_email_unique_constraint(db_session, test_email_list):
#     email = "duplicateuser@example.com"
#     test_email_list.append(email)

#     user1 = User(name="First User", email=email, password_hash="hash1")
#     user2 = User(name="Second User", email=email, password_hash="hash2")

#     db_session.add(user1)
#     await db_session.commit()

#     db_session.add(user2)
#     with pytest.raises(IntegrityError):
#         try:
#             await db_session.commit()
#         finally:
#             await db_session.rollback()
