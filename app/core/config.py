from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ekklesia Admin"
    environment: str = "development"

    database_url: AnyUrl = "postgresql+asyncpg://ekklesia:ekklesia@db:5432/ekklesia"
    master_database_url: AnyUrl = "postgresql+asyncpg://ekklesia:ekklesia@db_master:5432/ekklesia_master"

    secret_key: str = "CHANGE_ME"
    access_token_exp_minutes: int = 30
    refresh_token_exp_minutes: int = 60 * 24 * 30
    jwt_algorithm: str = "HS256"

    storage_path: str = "./storage"
    max_upload_mb: int = 10
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

