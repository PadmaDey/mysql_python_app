import os
from pydantic_settings import BaseSettings
from starlette.config import Config

# config = Config(env_file=".env")

from pathlib import Path

# Look for .env by walking up to 5 levels
env_path = next(
    (p / ".env" for p in Path(__file__).resolve().parents if (p / ".env").exists()),
    None,
)

if not env_path:
    import warnings
    warnings.warn("No .env file found while configuring settings.")
    env_path = ".env"  # fallback

config = Config(env_file=str(env_path))

class Settings(BaseSettings):
    """
    Add all the environment variables to the class
    """

    # Server Configs
    PORT: int = config("PORT", cast=int, default=8080)
    DEBUG: bool = config("DEBUG", cast=bool, default=False)

    # Database configs
    MYSQL_DATABASE: str = config("MYSQL_DATABASE", default='development')
    MYSQL_USER: str = config("MYSQL_USER", default='dev_user')
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default='qwerty')

    MYSQL_PORT: int = config("MYSQL_PORT", cast=int, default=3306)
    MYSQL_HOST: str = config("MYSQL_HOST", default="localhost")

    @property
    def ASYNC_DB_URL(self) -> str:
        actual_host = (
            "localhost" if os.getenv("ENV") == "local" else self.MYSQL_HOST
        )
        return (
            f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{actual_host}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )


settings = Settings()
