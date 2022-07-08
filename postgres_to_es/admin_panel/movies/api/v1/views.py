from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        films = Filmwork.objects.prefetch_related('genrefilmwork_set', 'personfilmwork_set')
        queryset = films.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg('genrefilmwork__genre__name', distinct=True),
            actors=ArrayAgg('personfilmwork__person__full_name',
                            filter=Q(personfilmwork__role=PersonFilmwork.RoleType.ACTOR), distinct=True),
            writers=ArrayAgg('personfilmwork__person__full_name',
                             filter=Q(personfilmwork__role=PersonFilmwork.RoleType.WRITER), distinct=True),
            directors=ArrayAgg('personfilmwork__person__full_name',
                               filter=Q(personfilmwork__role=PersonFilmwork.RoleType.DIRECTOR), distinct=True)
        )
        return queryset

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() is True else None,
            'next': page.next_page_number() if page.has_next() is True else None,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return kwargs.get('object', None)
