from pydantic_settings import BaseSettings
from starlette.config import Config

# config = Config("app/.env")
config = Config()


class Settings(BaseSettings):
    """
    Add all the environment variables to the class
    """

    # Server Configs
    PORT: int = config("PORT", cast=int, default=8080)
    DEBUG: bool = config("DEBUG", cast=bool, default=False)

    # Database configs
    MYSQL_DATABASE: str = config("MYSQL_DATABASE", default='test_database')
    MYSQL_USER: str = config("MYSQL_USER", default='emp_1')
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default='qwerty')

    # MYSQL_HOST: str = config("MYSQL_HOST", default="localhost")
    MYSQL_HOST: str = config("MYSQL_HOST", default="mysql")
    MYSQL_PORT: int = config("MYSQL_PORT", cast=int, default=3306)


settings = Settings()
