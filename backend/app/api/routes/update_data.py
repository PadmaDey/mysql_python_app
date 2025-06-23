from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.schemas import user as schemas
from app.db.dependencies import get_db
from app.models.user import User
from app.models.jti_blacklist import JTIBlacklist
from app.services.logger import logger
from app.core.auth.password import get_password_hash, verify_password
from app.core.auth.jwt_handler import create_access_token, get_current_user
from app.utils.validation import get_current_utc_time


router = APIRouter(prefix="/api/users", tags=["users"])

@router.put("/update-data", summary="update existing data")
async def update_data(update_user: schemas.Update_user, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        email = current_user["email"]
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid user mail"
            )
        
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        update_fields=dict()

        if update_user.name:
            update_fields["name"] = update_user.name

        if update_user.phone_no:
            update_fields["phone_no"] = update_user.phone_no

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Provided fields are not valid"
            )

        update_fields["updated_at"] = await get_current_utc_time()

        query = update(User).where(User.email == user.email).values(**update_fields)
        result = await db.execute(query)
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "msg": "User data updated successfully", 
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
                "msg":f"{e}", 
                "status": False
            }
        )