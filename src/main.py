import time
import os
import threading
import webbrowser
from fastapi import FastAPI, Path, Query, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager
import uvicorn
import logging
import colorlog

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.database import get_db
from routes import contacts, auth, users
from config.config import settings

logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.DEBUG if settings.app_mode == "dev" else logging.INFO)
handler = colorlog.StreamHandler()
handler.setLevel(logging.DEBUG if settings.app_mode == "dev" else logging.INFO)
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(yellow)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)
logger.addHandler(handler)


# @app.on_event("startup")
async def startup():
    """
    Function to initialize resources on application startup.

    This function initializes FastAPILimiter with a Redis connection.

    Returns:
    - None
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)
    logger.debug("startup done")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager to handle application lifespan events.

    This context manager initializes resources on application startup.

    Parameters:
    - app (FastAPI): The FastAPI application instance.

    Yields:
    - None

    Returns:
    - None
    """
    logger.debug("lifespan before")
    await startup()
    yield
    logger.debug("lifespan after")


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_files_path = os.path.join(os.path.dirname(__file__), "static")
# print("STATIC: ", static_files_path)
app.mount("/static", StaticFiles(directory=static_files_path), name="static")

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    """
    Route to render the home page.

    This route renders the index.html template as the home page.

    Parameters:
    - request (Request): The incoming request object.

    Returns:
    - HTMLResponse: HTML response containing the rendered template.
    """
    try:
        context = {"request": request, "title": "Home Page"}
        return templates.TemplateResponse("index.html", context)
    except Exception as e:
        print(f"Error rendering template: {e}")
        raise


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    Endpoint to check the health of the application.

    This endpoint checks the health of the application by querying the database.

    Parameters:
    - db (Session): Database session dependency.

    Returns:
    - dict: A dictionary containing a health message.
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI on Howe Work 11!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api")


# Function to open the web browser
def open_browser():
    """
    Function to open the web browser automatically.

    This function opens the web browser automatically when the application starts.

    Returns:
    - None
    """
    webbrowser.open("http://localhost:9000")


if __name__ == "__main__":
    # Start the web browser in a separate thread
    threading.Thread(target=open_browser).start()
    # Run the FastAPI application
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
