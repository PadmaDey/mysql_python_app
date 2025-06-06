from app.models import cursor
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from backend.app.services.logger import logger
from app.utils import serialize_row

def get_user(email: str):
    try:
        query = "SELECT * FROM users WHERE email = %s;"
        cursor.execute(query, (email,))
        raw_user = cursor.fetchone()

        if not raw_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return serialize_row(raw_user)

    except Exception as e:
        logger.error("Error: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": f"{e}", "status": False}
        )
