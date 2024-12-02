import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import django
from settings import logger
from backoff import backoff
from models import FilmWorkModel, ActorDTO, DirectorDTO, WriterDTO


root_project_path = Path(__file__).parent.parent
sys.path.append(str(root_project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings    # noqa: E402

# Check if DEBUG is set correctly
logger.info("Debug mode is %s", "ON" if settings.DEBUG else "OFF")


from movies.models import (     # noqa: E402
    FilmWork,
    Person,
    Genre,
    PersonFilmWork,
    GenreFilmWork
)


class PostgresExtractor:
    def __init__(self, chunk_size: int = 1, time_delta_sec: int = 0):
        self.chunk_size = chunk_size
        self.time_delta_sec = time_delta_sec
        self.model = None

    def fetch_data_in_chunks(self):
        time_delta = datetime.now(timezone.utc) - timedelta(seconds=self.time_delta_sec)
        queryset = self.model.objects.all().filter(modified__gte=time_delta)
        # Используем iterator() для "ленивой" итерации по объектам
        for obj in queryset.iterator(chunk_size=self.chunk_size):
            yield obj

    def get_modified_model(self, model):
        """
        Выгружаем чанк модифицированных данных модели из базы
        """
        self.model = model
        modified_models = []
        for obj in self.fetch_data_in_chunks():
            modified_models.append(obj)
        return modified_models

    @backoff()
    def extract_from_bd(self):
        modified_persons = self.get_modified_model(model=Person)
        person_film_works = []
        for person in modified_persons:
            person_film_works += FilmWork.objects.filter(
                    personfilmwork__person_id=person
                )

        modified_genres = self.get_modified_model(model=Genre)
        genre_film_works = []
        for genre in modified_genres:
            genre_film_works += FilmWork.objects.filter(
                    genrefilmwork__genre_id=genre
                )
        modified_films = self.get_modified_model(model=FilmWork)

        modified_data = modified_films + person_film_works + genre_film_works

        logger.debug(len(modified_data), modified_data)

        results = []
        for film_work in modified_data:
            actors = self.fetch_related_entities(film_work.id, 'actor')
            directors = self.fetch_related_entities(film_work.id, 'director')
            writers = self.fetch_related_entities(film_work.id, 'writer')

            film_work_data = FilmWorkModel(
                id=film_work.id,
                title=film_work.title,
                description=film_work.description,
                creation_date=str(film_work.creation_date),
                rating=film_work.rating,
                type=film_work.type,
                genres=list(film_work.genres.values_list('name', flat=True)),
                actors=[ActorDTO(**actor) for actor in actors],
                directors=[DirectorDTO(**director) for director in directors],
                writers=[WriterDTO(**writer) for writer in writers],
                directors_names=[x['person__full_name'] for x in directors],
                writers_names=[x['person__full_name'] for x in writers],
                actors_names=[x['person__full_name'] for x in actors]
            )
            results.append(film_work_data.dict())

        return results

    @staticmethod
    def fetch_related_entities(self, film_work_id, role):
        """Извлекает связанные объекты (actors/directors/writers) по полю role."""
        return list(PersonFilmWork.objects.filter(
            film_work=film_work_id,
            role=role
        ).select_related('person').values('person__id', 'person__full_name'))
