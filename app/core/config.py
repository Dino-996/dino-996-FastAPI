from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """ Automatically read variables from the .env file """
    app_name: str
    description: str
    version: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")

# Singleton
settings = Settings() #type: ignore
