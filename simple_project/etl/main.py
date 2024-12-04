import time
import datetime
from extract import PostgresExtractor
from settings import Settings, logger, state
from es_load import ElasticsearchLoader

settings = Settings()
logger.debug("Settings loaded: %s", settings.model_dump())


def check_time_delta_sec():
    state_time = state.get_state('last_processed_ts')
    logger.debug("last_processed_ts '%s'", state_time)

    index_created_ts = state.get_state('index_created_ts')
    logger.debug("index_created_ts '%s'", index_created_ts)

    if state_time:
        last_processed_ts = datetime.datetime.strptime(state_time, '%Y-%m-%d %H:%M:%S.%f')
        time_delta_sec = (datetime.datetime.now() - last_processed_ts).total_seconds()
        if time_delta_sec > settings.TIME_DELTA:
            return time_delta_sec
        else:
            return settings.TIME_DELTA

    if not index_created_ts:
        return (datetime.datetime.now() - datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()

    if index_created_ts and not state_time:
        time_delta_sec = (datetime.datetime.now() - index_created_ts).total_seconds()
        return time_delta_sec


def main():
    es_index = settings.INDEX_NAME
    es_url = settings.ES_URL
    es = ElasticsearchLoader(es_url=es_url, index_name=es_index)
    time_delta_sec = check_time_delta_sec()

    while True:
        logger.debug('time_delta_sec = %s', time_delta_sec)
        chunk_size = settings.CHUNK_SIZE
        pg_ex = PostgresExtractor(chunk_size=chunk_size, time_delta_sec=time_delta_sec)
        data_chunk = pg_ex.extract_from_bd()

        logger.info("Film works to load: %s", len(data_chunk))

        for film_work_data in data_chunk:
            logger.info(film_work_data)

        if es.elasticsearch_load(data_chunk):
            state.set_state('last_processed_ts', str(datetime.datetime.now()))
            logger.info("last_processed_ts '%s'", state.get_state('last_processed_ts'))

        time_delta_sec = settings.TIME_DELTA

        time.sleep(settings.TIME_DELTA)


if __name__ == '__main__':
    main()
