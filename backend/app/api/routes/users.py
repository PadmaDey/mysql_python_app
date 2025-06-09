from app.schemas import user as schemas
from app.db.connection import conn, cursor
from app.utils.validation import get_current_utc_time, serialize_row
from app.core.auth.password import get_password_hash, verify_password
from fastapi import APIRouter, HTTPException, status, Path, Depends
from fastapi.responses import JSONResponse
from app.services.logger import logger
from app.core.auth.jwt_handler import create_access_token, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/signup", summary="Add a new user")
async def signup_user(user: schemas.User):
    try:
        payload = user.model_dump()

        payload["password"] = get_password_hash(payload.get("password"))

        c_time = get_current_utc_time()
        payload["created_at"] = c_time
        payload["updated_at"] = c_time

        cursor.execute(
            "INSERT INTO users (name, email, phone_no, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                payload.get("name"),
                payload.get("email"),
                payload.get("phone_no"),
                payload.get("password"),
                payload.get("created_at"),
                payload.get("updated_at"),
            ),
        )
        conn.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"msg": "User created successfully", "status": True})
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})


@router.post("/login", summary="User logging in")
async def login_user(user: schemas.Login):
    try:
        query = "select * from users where email = %s;"
        cursor.execute(query, (user.email,))
        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        hashed_password = db_user[4] 

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
        token = create_access_token({"email": user.email}, timedelta(minutes=15))

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"token": token, "msg": "User logged in successfully", "status": True})
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})


@router.get("/", summary="Get all users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    try:
        cursor.execute("select * from users;")
        raw_users = cursor.fetchall()
        users = [serialize_row(row) for row in raw_users]

        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "data": users})
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})


@router.get("/{name}", summary="Get a particular users")
async def get_particular_user(name: str = Path(..., description="Name of the User", example="Test")): # , sort_by: str = Query(..., description="Sort by Name", order: str = Query('asc', description='sort in asc or desc order')
    user= None
    try:
        name = name.strip().title()
        query = "select * from users where name = %s;"
        cursor.execute(query,(name,))
        raw_user = cursor.fetchone()
        if not raw_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = serialize_row(raw_user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "data": user})
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})



@router.put("/update-data", summary="update existing data")
async def update_data(user: schemas.Update_user, current_user: dict = Depends(get_current_user)):
    try:
        cursor.execute("select * from users where email = %s", (current_user,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

        update_fields=[]
        values=[]

        if user.name is not None:
            update_fields.append("name = %s")
            values.append(user.name)

        if user.phone_no is not None:
            update_fields.append("phone_no = %s")
            values.append(user.phone_no)

        if not update_fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided fields are not valid")

        update_fields.append("updated_at = %s")
        values.append(get_current_utc_time())

        query = f"update users set {', '.join(update_fields)} where email = %s;"
        values.append(current_user)
        cursor.execute(query, tuple(values))
        conn.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "User data updated successfully", "status": True})
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg":f"{e}", "status": False})



@router.delete("/delete-data", summary="Delete a user data")
async def del_user(current_user: dict = Depends(get_current_user)):
    try:
        cursor.execute("select * from users where email = %s", (current_user,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

        query = "delete from users where email= %s;"
        cursor.execute(query, (current_user,))
        conn.commit()
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "User deleted successfully", "status": True})
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg":f"{e}", "status": False})


