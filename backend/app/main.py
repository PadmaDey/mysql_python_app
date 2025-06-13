import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import api_router
from app.core.config import settings
from app.services.logger import logger
from app.db import initialize_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App is starting... initializing database.")
    await initialize_db()
    logger.info("Database initialized")
    yield
    logger.info("App is shutting down...")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
def read_root():
    logger.info("route is working fine!")
    return {"msg": "ok"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        debug=settings.DEBUG
        )



