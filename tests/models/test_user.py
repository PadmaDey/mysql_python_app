import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from tests.conftest import register_test_email

@pytest.mark.asyncio
async def test_create_user(db_session):
    email = "unittestuser@example.com"
    await register_test_email(email)

    user = User(
        name="Unit User",
        email=email,
        phone_no=1234567890,
        password_hash="hashed_pass"
    )

    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == email))
    saved_user = result.scalar_one_or_none()

    assert saved_user is not None
    assert saved_user.name == "Unit User"
    assert saved_user.phone_no == 1234567890
    assert saved_user.password_hash == "hashed_pass"
    assert saved_user.created_at is not None
    assert saved_user.updated_at is not None


@pytest.mark.asyncio
async def test_email_unique_constraint(db_session):
    email = "duplicateuser@example.com"
    await register_test_email(email)

    user1 = User(
        name="First User",
        email=email,
        password_hash="hash1"
    )
    user2 = User(
        name="Second User",
        email=email,
        password_hash="hash2"
    )

    db_session.add(user1)
    await db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        try:
            await db_session.commit()
        finally:
            # Critical: rollback to reset session state after failed commit
            await db_session.rollback()
