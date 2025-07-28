from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.user import User
from app.services.logger import logger
from app.auth.jwt_handler import get_current_user


router = APIRouter(prefix="/api/users", tags=["users"])

@router.delete("/delete-data", status_code=status.HTTP_200_OK, summary="Delete a user data")
async def del_user(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
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

        query = delete(User).where(User.email == email)
        result = await db.execute(query)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "msg": "User deleted successfully", 
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