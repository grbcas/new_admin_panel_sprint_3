import time
import datetime
from extract import PostgresExtractor
from state import JsonFileStorage, State
from settings import logger, ROOT_DIR
from es_load import ElasticsearchLoader
import settings


file_path = "/app/state.json"
storage = JsonFileStorage(file_path=file_path)
logger.warning("State storage created %s.", file_path)
state = State(storage=storage)


def check_time_delta_sec():
    if state.get_state('time_delta_sec'):
        return state.get_state('time_delta_sec')

    state_time = state.get_state('last_processed_time')
    if not state_time:
        logger.warning("No last processed time found; using current time as fallback.")
        return settings.TIME_DELTA

    logger.info("last_processed_time '%s'", state_time)
    last_processed_time = datetime.datetime.strptime(state_time, '%Y-%m-%d %H:%M:%S.%f')
    time_delta_sec = (datetime.datetime.now() - last_processed_time).total_seconds()
    if time_delta_sec > settings.TIME_DELTA:
        return time_delta_sec
    else:
        return settings.TIME_DELTA


def main():
    es_index = settings.INDEX_NAME
    es_url = settings.ES_URL
    es = ElasticsearchLoader(es_url=es_url, index_name=es_index)

    time_delta_sec = check_time_delta_sec()

    while True:
        logger.debug('time_delta_sec >>> %s', time_delta_sec)
        chunk_size = settings.CHUNK_SIZE
        pg_ex = PostgresExtractor(chunk_size=chunk_size, time_delta_sec=time_delta_sec)
        data_chunk = pg_ex.extract_from_bd()

        logger.info("Film works to load: %s", len(data_chunk))

        for film_work_data in data_chunk:
            logger.info(film_work_data)

        if es.elasticsearch_load(data_chunk):
            state.set_state('last_processed_time', str(datetime.datetime.now()))
            logger.info("last_processed_time '%s'", state.get_state('last_processed_time'))

        time_delta_sec = settings.TIME_DELTA

        time.sleep(settings.TIME_DELTA)


if __name__ == '__main__':
    main()
