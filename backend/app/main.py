import uvicorn
from fastapi import FastAPI
from app.api import api_router
from app.core.config import settings
from app.services.logger import logger


app = FastAPI()
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



