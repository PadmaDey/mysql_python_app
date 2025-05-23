import uvicorn
from app import schemas
from app.config import settings
from app.db import conn, cursor
from app.utils import get_current_utc_time, get_password_hash, verify_password
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from datetime import datetime

app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "ok"}


@app.post("/api/users/add", summary="Add a new user")
async def add_user(user: schemas.User):
    try:
        payload = user.model_dump()

        # Validation
        if len(payload.get("name")) <= 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name should be at least 2 characters")

        if "@" not in payload.get("email"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")

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
        print(f"Error: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False})

def serialize_row(row):
    return [
        item.isoformat() if isinstance(item, datetime) else item
        for item in row
    ]

@app.get("/api/users/get-all", summary="Get all users")
async def get_all_users():
    try:
        print("test")
        cursor.execute("SELECT * FROM users;")
        raw_users = cursor.fetchall()
        users = [serialize_row(row) for row in raw_users]
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "data": users})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"msg": f"{e}", "status": False, "data": users})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
