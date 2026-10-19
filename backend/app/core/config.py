from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "spendar"

    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    SESSION_EXPIRE_MINUTES: int = 1440
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    SESSION_COOKIE_NAME: str = "session_id"

    @property
    def database_url(self) -> URL:
        # URL.create escapes special characters in the password for us.
        return URL.create(
            "mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": "utf8mb4"},
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
