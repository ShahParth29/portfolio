from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    SECRET_KEY: str = "INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "INSECURE-DEV-PASSWORD-CHANGE-IN-PRODUCTION"

    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_TO: str = "shahparth29980@gmail.com"
    UPLOAD_DIR: str = "frontend/uploads"

    # Storage backend: "local" or "cloudinary"
    STORAGE_BACKEND: str = "local"

    # Cloudinary (required when STORAGE_BACKEND=cloudinary)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Security
    CORS_ORIGINS: str = "*"  # Comma-separated origins for production
    LOGIN_RATE_LIMIT: int = 5  # Max login attempts per minute per IP

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
