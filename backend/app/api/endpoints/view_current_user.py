from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.user import User
from app.services.logger import logger
from app.auth.jwt_handler import get_current_user


router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", summary="Get current logged-in user")
async def get_current_user_data(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
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

        users_data ={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_no": user.phone_no,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

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
        logger.error("Error fetching current user: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={
                "msg": str(e),
                "status": False
            }
        )