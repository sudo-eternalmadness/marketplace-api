from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    db_url: str = "sqlite:///./db.sqlite3"
    app_name: str = "Marketplace API"
    access_token_expire_minutes: float = 15
    secret_key: SecretStr


settings = Settings()
