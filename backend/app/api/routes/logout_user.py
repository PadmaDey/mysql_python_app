from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.jti_blacklist import JTIBlacklist
from app.services.logger import logger
from app.core.auth.jwt_handler import get_current_user


router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/log-out", status_code=status.HTTP_200_OK, summary="Logout current user")
async def logout_user(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        jti = current_user.get("jti") 
        if not jti:
            raise HTTPException(
                status_code=400, 
                detail="JTI not found in token"
            )

        # Check for duplicate JTI
        query = select(JTIBlacklist).where(JTIBlacklist.jti == jti)
        result = await db.execute(query)
        existing_jti = result.scalar_one_or_none()

        if existing_jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate JTI: Token already blacklisted"
            )

        # Add the JTI to the blacklist
        token_blacklist = JTIBlacklist(jti=jti)
        db.add(token_blacklist)
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "msg": "User logged out successfully", 
                "status": True
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Logout error: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "msg": f"An unexpected error occurred: {e}", 
                "status": False
            }
        )