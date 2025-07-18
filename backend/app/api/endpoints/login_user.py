from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.schemas import user as schemas
from app.db.dependencies import get_db
from app.models.user import User
from app.services.logger import logger
from app.auth.password import verify_password
from app.auth.jwt_handler import create_access_token


router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/login", status_code=status.HTTP_200_OK, summary="User logging in")
async def login_user(user: schemas.Login, db: AsyncSession = Depends(get_db)):
    try:
        query = select(User).where(User.email == user.email)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            ) 

        if not await verify_password(user.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Incorrect password"
            )
    
        token = await create_access_token({"email": user.email}, timedelta(minutes=15))

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "token": token, 
                "msg": "User logged in successfully", 
                "status": True
            }
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