from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Sistema de Gestión de Citas Médicas"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "medical_appointments"


settings = Settings()
