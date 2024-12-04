import logging
import os
from dotenv import load_dotenv

from pathlib import Path

# Централизованно задаём основные пути.
ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / 'config'


load_dotenv()

logger = logging.getLogger("film_works_logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

BUTCH_SIZE = int(os.environ.get("BUTCH_SIZE"))

ES_URL = os.environ.get("ES_URL")

TABLES_TO_CHECK = ["film_work", "person", "genre"]

INDEX_NAME = os.environ.get("INDEX_NAME")
TIME_DELTA = int(os.environ.get("TIME_DELTA"))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
