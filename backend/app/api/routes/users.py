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


@router.post("/login", summary="User logging in")
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
            status_code=status.HTTP_201_CREATED, 
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



@router.delete("/delete-data", summary="Delete a user data")
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


@router.post("/log-out", summary="Logout current user")
async def logout_user(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        jti = current_user.get("jti") 
        if not jti:
            raise HTTPException(
                status_code=400, 
                detail="JTI not found in token"
            )

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

