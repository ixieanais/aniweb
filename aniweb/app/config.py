import os
from pathlib import Path
from dotenv import load_dotenv

ANIWEB_PATH = Path(os.getcwd()).parent
PARENT_PATH = ANIWEB_PATH.parent
STATIC_PATH = ANIWEB_PATH / "static"
TEMPLATES_PATH = ANIWEB_PATH / "templates"
UPDATE_TIME = 1800 # 30m
SESSION_MAX_AGE = 2592000
SESSION_NAME = "session_id"

load_dotenv(PARENT_PATH / ".env")

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
DATABASE_URL_psycopg = DATABASE_URL.replace("asyncpg", "psycopg")