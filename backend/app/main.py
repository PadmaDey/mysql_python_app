import uvicorn
from app import schemas
from app.config import settings
from app.db import conn, cursor
from app.utils import get_current_utc_time, get_password_hash, verify_password, serialize_row
from fastapi import FastAPI, HTTPException, status, Path, Query, Depends
from fastapi.responses import JSONResponse
from app.logger import logger
from app.auth import create_access_token, decode_access_token, oauth2_scheme, get_curent_user

from datetime import datetime, timedelta

app = FastAPI()


@app.get("/")
def read_root():
    logger.info("route is working fine!")
    return {"msg": "ok"}


@app.post("/api/users/signup", summary="Add a new user")
async def add_user(user: schemas.User):
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


@app.post("/api/users/login", summary="User logging in")
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


# @app.post("/api/users/verify-user", summary="Verifying the logged in credential matching with stored credential")
# async def verify_user(user: schemas.VerifyUser):
#     try:
#         payload = decode_access_token(user.token)
#         if not payload:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired")
        
#         email = payload.get("email")
#         if not email:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User email unauthorised")
        
#         query = "select * from users where email = %s"
#         cursor.execute(query, (email,))

#         db_user = cursor.fetchone()
#         serialized_user =serialize_row(db_user)
#         if not db_user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details= "User data not found")
        
#         return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "data": serialized_user})

#     except Exception as e:
#         logger.error("Error: %s", e)
#         return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})


@app.get("/api/users", summary="Get all users")
async def get_all_users(current_user: dict = Depends(get_curent_user)):
    try:
        cursor.execute("select * from users;")
        raw_users = cursor.fetchall()
        users = [serialize_row(row) for row in raw_users]

        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "data": users})
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})


@app.get("/api/users/{name}", summary="Get a particular users")
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



@app.put("/api/users/update-data", summary="update existing data")
async def update_data(user: schemas.Update_user, current_user: dict = Depends(get_curent_user)):
    try:
        cursor.execute("select * from users where email = %s", (current_user,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

        update_fields=[]
        values=[]
        update_fields.append("name = %s")
        values.append(user.name)

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



@app.delete("/api/users/delete-data", summary="Delete a user data")
async def del_user(user: schemas.Delete_user):
    try:
        cursor.execute("select * from users where email = %s", (user.email,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

        query = "delete from users where email= %s;"
        cursor.execute(query, (user.email,))
        conn.commit()
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "User deleted successfully", "status": True})
    
    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg":f"{e}", "status": False})





if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)



