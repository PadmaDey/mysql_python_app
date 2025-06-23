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

@router.get("/", summary="Get all users")
async def get_all_users(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        email = current_user["email"]
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid user session"
            )

        query = select(User)
        result = await db.execute(query)
        users = result.scalars().all()

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No users found"
            )

        users_data =[{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone_no": u.phone_no,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        } for u in users]

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "status": True, 
                "data": users_data
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