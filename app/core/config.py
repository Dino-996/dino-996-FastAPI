from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """ Automatically read variables from the .env file """
    app_name: str | None = None
    description: str | None = None
    version: str | None = None
    secret_key: str | None = None
    algorithm: str | None = None
    access_token_expire_minutes: int | None = None
    refresh_token_expire_days: int | None = None
    database_password: str | None = None
    database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

# Singleton
settings = Settings()
