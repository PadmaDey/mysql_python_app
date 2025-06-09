from app.db.connection import cursor
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.services.logger import logger
from app.utils.validation import serialize_row

def get_user(email: str):
    try:
        query = "SELECT * FROM users WHERE email = %s;"
        cursor.execute(query, (email,))
        raw_user = cursor.fetchone()

        if not raw_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return serialize_row(raw_user)
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error("Error: %s", e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
