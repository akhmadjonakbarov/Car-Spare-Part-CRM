from pydantic_settings import BaseSettings
from dotenv import load_dotenv

import os

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Store Manager"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str = ""
    API_V1: str = "/api/v1"
    API_V2: str = "/api/v2"
    TIME_ZONE: str = 'Asia/Tashkent'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 120
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = "HS256"
    ADMIN_EMAIL: str = "akhmadjonakbarov@gmail.com"
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    FILES_DIR: str = 'ds_files'
    DEBUG: bool = False
    TESTING: bool = False


settings = Settings()
