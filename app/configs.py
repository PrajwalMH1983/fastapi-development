from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str = "localhost"
    database_username: str = "postgres"
    database_name: str
    secret_key: str = "234ui234567532"
    algorithm: str
    access_token_expire_minutes: str

    class Config:
        env_file = ".env"

settings = Settings()
