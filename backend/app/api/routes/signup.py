from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import user as schemas
from app.db.dependencies import get_db
from app.models.user import User
from app.services.logger import logger
from app.core.auth.password import get_password_hash


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/signup", summary="Add a new user")
async def signup_user(user: schemas.User, db: AsyncSession = Depends(get_db)):
    try:
        hashed_password = await get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            phone_no=user.phone_no,
            password_hash=hashed_password,
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={
                    "msg": "User created successfully", 
                    "status": True
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="A user with this mail already exists."
            )
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={
                "msg": f"{e}", 
                "status": False
            }
        )