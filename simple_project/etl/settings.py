import logging
from pydantic_settings import BaseSettings
from pathlib import Path
from state import JsonFileStorage, State


class Settings(BaseSettings):
    """Класс для хранения настроек приложения."""
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    BATCH_SIZE: int
    ES_URL: str
    INDEX_NAME: str
    TIME_DELTA: int
    CHUNK_SIZE: int
    PYTHONPATH: str
    DEBUG: bool


settings = Settings()

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / 'config'

log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logger = logging.getLogger("film_works_logger")

logger.setLevel(log_level)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

file_path = f"{ROOT_DIR}/state.json"
storage = JsonFileStorage(file_path=file_path)
state = State(storage=storage)
logger.info("State storage created %s.", file_path)
