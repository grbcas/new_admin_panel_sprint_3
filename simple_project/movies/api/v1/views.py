from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.db.models import Prefetch

from movies.models import FilmWork, PersonFilmWork, Genre, Person


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_queryset(self):
        return FilmWork.objects.prefetch_related(
            Prefetch('genres', queryset=Genre.objects.only('name')),
            Prefetch('persons', queryset=Person.objects.only('full_name'))
        ).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )

        results = []
        for filmwork in queryset:

            actors = list(PersonFilmWork.objects.select_related().filter(
                film_work=filmwork.id).filter(
                role='actor').values_list(
                'person__full_name', flat=True)
            )
            directors = list(PersonFilmWork.objects.select_related().filter(
                film_work=filmwork.id).filter(
                role='director').values_list(
                'person__full_name', flat=True)
            )
            writers = list(PersonFilmWork.objects.select_related().filter(
                film_work=filmwork.id).filter(
                role='writer').values_list(
                'person__full_name', flat=True)
            )

            filmwork_data = {
                'id': filmwork.id,
                'title': filmwork.title,
                'description': filmwork.description,
                'creation_date': filmwork.creation_date,
                'rating': filmwork.rating,
                'type': filmwork.type,
                'genres': list(filmwork.genres.values_list('name', flat=True)),
                'actors': actors,
                'directors': directors,
                'writers': writers,
            }
            results.append(filmwork_data)

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': results,
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        genres = list(obj.genres.values_list('name', flat=True))

        actors = list(
            PersonFilmWork.objects.select_related().filter(
                film_work=obj.id).filter(
                role='actor').values_list(
                'person__full_name', flat=True)
        )

        writers = list(
            PersonFilmWork.objects.select_related().filter(
                film_work=obj.id).filter(
                role='writer').values_list(
                'person__full_name', flat=True)
        )

        directors = list(
            PersonFilmWork.objects.select_related().filter(
                film_work=obj.id).filter(
                role='director').values_list(
                'person__full_name', flat=True)
        )

        # сериализация объекта в словарь
        context = {
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "creation_date": obj.creation_date,
            "rating": obj.rating,
            "type": obj.type,
            "genres": genres,
            "actors": actors,
            "directors": directors,
            "writers": writers,
        }

        return context
