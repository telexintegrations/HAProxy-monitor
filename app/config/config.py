#!/usr/bin/python
"""sets environment variable using pydantic BaseSettings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """contains all required env settings loaded from .env"""

    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8")

   #
   


settings = Settings()
