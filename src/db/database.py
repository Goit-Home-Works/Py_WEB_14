"""
This script sets up a SQLAlchemy database connection and provides a FastAPI dependency function for obtaining a database session.

It first loads environment variables from a .env file using dotenv. It expects the following environment variables to be set:
- POSTGRES_HOST: The PostgreSQL host address.
- POSTGRES_USERNAME: The username for accessing the PostgreSQL database.
- POSTGRES_PASSWORD: The password for accessing the PostgreSQL database.
- POSTGRES_PORT: The port number for the PostgreSQL database.
- POSTGRES_DATABASE: The name of the PostgreSQL database.

It then constructs a SQLAlchemy database URI using the provided environment variables. If any of the required environment variables are missing, it raises an AssertionError.

Finally, it creates an engine for the database connection and a sessionmaker for creating database sessions. It also defines a FastAPI dependency function get_db() that yields a database session. If any SQLAlchemy error occurs during database operations, it rolls back the transaction and raises a FastAPI HTTPException with status code 400 and the error details.

Usage:
- Call the get_db() function to obtain a database session within FastAPI route functions.
- When running this script directly (__name__ == "__main__"), it prints the database engine.
"""
from pathlib import Path
from fastapi import HTTPException, status
from dotenv import load_dotenv

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

domain = os.getenv("POSTGRES_HOST")
if not domain:
    ENV_FILE = Path(__file__).resolve().parent.parent.parent.joinpath(".env")
    load_dotenv(ENV_FILE)
    domain = os.getenv("POSTGRES_HOST")
    print(f"{ENV_FILE=} {domain=}")

username = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
domain = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DATABASE")

URI = None
if domain:
    URI = f"postgresql+psycopg2://{username}:{password}@{domain}:{port}/{database}"

SQLALCHEMY_DATABASE_URL = URI

print(f"{SQLALCHEMY_DATABASE_URL=}")
print(f"{port=}")

assert SQLALCHEMY_DATABASE_URL is not None, "SQLALCHEMY_DATABASE_URL UNDEFINED"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    FastAPI dependency function for obtaining a database session.

    Yields:
        session: SQLAlchemy database session.

    Raises:
        HTTPException: If any SQLAlchemy error occurs during database operations, it rolls back the transaction and raises an HTTPException with status code 400 and the error details.
    """
    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        print(err)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()


if __name__ == "__main__":
    print(engine)
