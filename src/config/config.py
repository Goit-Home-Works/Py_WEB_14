from os import environ
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_PATH.joinpath(".env"))
APP_ENV = environ.get("APP_ENV")
print(f"{BASE_PATH=}")
print(f"{APP_ENV=}")

# Debugging: Print the values of the environment variables
print(f"POSTGRES_USERNAME={environ.get('POSTGRES_USERNAME')}")
print(f"POSTGRES_PASSWORD={environ.get('POSTGRES_PASSWORD')}")
print(f"POSTGRES_PORT={environ.get('POSTGRES_PORT')}")
print(f"POSTGRES_DATABASE={environ.get('POSTGRES_DATABASE')}")


class Settings(BaseSettings):
    app_mode: str = "prod"
    app_name: str = "contacts"
    app_host: str = "0.0.0.0"
    app_port: int = 9000
    token_secret_key: str = "some_SuPeR_key"
    token_algorithm: str = "HS256"
    mail_username: str = "user@example.com"
    mail_password: str = ""
    mail_from: str = "user@example.com"
    mail_port: int = 465
    mail_server: str = ""
    mail_from_name: str = ""
    redis_host: str = "localhost"
    redis_port: int = 6379
    cloudinary_name: str = "some_name"
    cloudinary_api_key: str = "0000000000000"
    cloudinary_api_secret: str = "some_secret"
    create_limiter_times: int = 2
    create_limiter_seconds: int = 5
    sendgrid_api_key: str = ""

    class Config:
        extra = "ignore"
        env_file = BASE_PATH.joinpath(f".env-{APP_ENV}") if APP_ENV else BASE_PATH.joinpath(".env")
        env_file_encoding = "utf-8"

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+psycopg2://{environ.get('POSTGRES_USERNAME')}:{environ.get('POSTGRES_PASSWORD')}@localhost:{environ.get('POSTGRES_PORT')}/{environ.get('POSTGRES_DATABASE')}"

settings = Settings()

if __name__ == "__main__":
    print(f"{settings.Config.env_file=}")
    print(f"{settings=}")
