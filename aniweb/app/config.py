from os import getcwd, makedirs
from pathlib import Path

ANIWEB_PATH = Path(getcwd()).parent
PARENT_PATH = ANIWEB_PATH.parent
DATA_PATH = PARENT_PATH / "data"
DATABASE_PATH = DATA_PATH / "database.db"
STATIC_PATH = ANIWEB_PATH / "static"
TEMPLATES_PATH = ANIWEB_PATH / "templates"
UPDATE_TIME = 1800 # 30m

makedirs(DATA_PATH, exist_ok=True)