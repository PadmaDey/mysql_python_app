from pydantic import BaseSettings
from starlette.config import Config

config = Config(".env")


class Settings(BaseSettings):
    """
    Add all the environment variables to the class
    """

    # Server Configs
    PORT: int = config("PORT", default=8000)
    DEBUG: bool = config("DEBUG", default=False)

    # Database configs
    MYSQL_DATABASE: str = config("MYSQL_DATABASE")
    MYSQL_USER: str = config("MYSQL_USER")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD")

    MYSQL_HOST: str = config("MYSQL_HOST", default="mysql")
    MYSQL_PORT: int = config("MYSQL_PORT", default=3306)


settings = Settings()
