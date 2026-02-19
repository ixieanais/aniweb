import os
from pathlib import Path

ANIWEB_PATH = Path(os.getcwd()).parent
PARENT_PATH = ANIWEB_PATH.parent
DATA_PATH = PARENT_PATH / "data"
DATABASE_PATH = DATA_PATH / "database.db"
STATIC_PATH = ANIWEB_PATH / "static"
TEMPLATES_PATH = ANIWEB_PATH / "templates"
UPDATE_TIME = 1800 # 30m
SESSION_MAX_AGE = 2592000
SESSION_NAME = "session_id"

os.makedirs(DATA_PATH, exist_ok=True)