from backoff import backoff
from elasticsearch import Elasticsearch, ConnectionError
from elasticsearch.helpers import bulk
from settings import logger, ROOT_DIR
import datetime
from state import State, JsonFileStorage


class ElasticsearchLoader:
    def __init__(self, es_url: str, index_name: str):
        self.es_url = es_url
        self.index_name = index_name
        self.es = None

        try:
            self.es = self.connect_elasticsearch()
        except Exception as ex:
            logger.error("Failed to connect to Elasticsearch: %s", ex)

    @backoff()
    def connect_elasticsearch(self) -> Elasticsearch:
        """Устанавливает соединение с сервером Elasticsearch."""
        try:
            es = Elasticsearch(self.es_url)
            if not es.indices.exists(index=self.index_name):
                self.create_index(es)
            else:
                logger.info("Index '%s' already exists.", self.index_name)
            return es
        except ConnectionError as ex:
            logger.error("Connection error with Elasticsearch: %s", ex)
            raise

    @backoff()
    def create_index(self, es: Elasticsearch):
        """Создает индекс в Elasticsearch, используя указанную схему."""
        try:
            with open(f"{ROOT_DIR}/es_schema.json", "r", encoding="utf8") as file:
                schema = file.read()
                es.indices.create(index=self.index_name, body=schema)
                logger.info(" Create Index '%s' was created.", self.index_name)

                current_time = datetime.datetime.now()
                unix_epoch = datetime.datetime(1970, 1, 1)
                time_delta_sec = (current_time - unix_epoch).total_seconds()
                logger.info("New ES index: setting time_delta_sec from the unix_epoch start: %s", time_delta_sec)

                file_path = "/app/state.json"
                storage = JsonFileStorage(file_path=file_path)
                logger.warning("State storage created %s.", file_path)
                state = State(storage=storage)
                state.set_state('time_delta_sec', time_delta_sec)

        except ConnectionError as ex:
            logger.error("Failed to create index '%s': %s", self.index_name, ex)

    @backoff()
    def elasticsearch_load(self, data: list):
        """Загрузка данных в Elasticsearch методом bulk."""
        if not self.es:
            logger.error("Elasticsearch connection is not established.")
            return None

        actions = [
            {
                "_index": self.index_name,
                "_id": document["id"],
                "_source": document,
            }
            for document in data
        ]

        try:
            success, _ = bulk(self.es, actions)
            logger.info("Successfully uploaded %d documents to Elasticsearch.", success)
            return success
        except Exception as ex:
            logger.error("Failed to upload data to Elasticsearch: %s", ex)
            raise
