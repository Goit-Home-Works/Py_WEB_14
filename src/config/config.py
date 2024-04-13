from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ConfigDict, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict



BASE_PATH_PROJECT = Path(__file__).resolve().parent.parent
print(f"{BASE_PATH_PROJECT=}")
BASE_PATH = BASE_PATH_PROJECT.parent
print(f"{BASE_PATH=}")
load_dotenv(BASE_PATH.joinpath(".env"))
APP_ENV = environ.get("APP_ENV")
print(f"{APP_ENV=}")

# Debugging: Print the values of the environment variables
print(f"POSTGRES_USERNAME={environ.get('POSTGRES_USERNAME')}")
print(f"POSTGRES_PASSWORD={environ.get('POSTGRES_PASSWORD')}")
print(f"POSTGRES_PORT={environ.get('POSTGRES_PORT')}")
print(f"POSTGRES_DATABASE={environ.get('POSTGRES_DATABASE')}")

class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     extra="ignore",
    #     env_file=BASE_PATH.joinpath(f".env-{APP_ENV}") if APP_ENV else BASE_PATH.joinpath(".env"),
    #     env_file_encoding="utf-8",
    # )
    app_mode: str = "prod"
    app_version: str = "hw"
    app_name: str = "contacts"
    app_host: str = "0.0.0.0"
    app_port: int = 9000
    # sqlalchemy_database_url: str | None = None
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
    redis_password: str = ""
    cloudinary_name: str = "some_name"
    cloudinary_api_key: str = "0000000000000"
    cloudinary_api_secret: str = "some_secret"
    reate_limiter_times: int = 2
    reate_limiter_seconds: int = 5
    SPHINX_DIRECTORY: str = str(BASE_PATH_PROJECT.joinpath("docs", "_build", "html"))
    STATIC_DIRECTORY: str = str(BASE_PATH_PROJECT.joinpath("static"))

    sendgrid_api_key: str = ""

    class Config:
        extra = "ignore"
        env_file = BASE_PATH.joinpath(f".env-{APP_ENV}") if APP_ENV else BASE_PATH.joinpath(".env")
        env_file_encoding = "utf-8"

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+psycopg2://{environ.get('POSTGRES_USERNAME')}:{environ.get('POSTGRES_PASSWORD')}@localhost:{environ.get('POSTGRES_PORT')}/{environ.get('POSTGRES_DATABASE')}"

settings = Settings()

settings=Settings(
    app_mode='dev',
    app_version='hw',
    app_name='contacts',
    app_host='0.0.0.0',
    app_port=9000,
    token_secret_key='mysecret123',
    token_algorithm='HS256',
    mail_username='vicky23@meta.ua',
    mail_password='Testfastaoi23',
    mail_from='vicky23@meta.ua', mail_port=465, mail_server='smtp.meta.ua', mail_from_name='TODO System', redis_host='localhost', redis_port=6379, redis_password='', cloudinary_name='ddgxvfauw', cloudinary_api_key='898426416919869', cloudinary_api_secret='_uYEk-__x07JTk8JJgHW7hZoOrQ', reate_limiter_times=2, reate_limiter_seconds=5, SPHINX_DIRECTORY='/home/sergio/Desktop/Py_WEB_14/src/docs/_build/html', STATIC_DIRECTORY='/home/sergio/Desktop/Py_WEB_14/src/static', sendgrid_api_key='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')


if __name__ == "__main__":
    print(f"{settings.Config.env_file=}")
    print(f"{settings=}")
