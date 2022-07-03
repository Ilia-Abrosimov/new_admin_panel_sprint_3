import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)

    class Meta:
        db_table = 'content\".\"genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full name'), max_length=255)

    class Meta:
        db_table = 'content\".\"person'
        ordering = ['-created']
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmType(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV show')
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateField(_('creation_date'), null=True, blank=True)
    file_path = models.TextField(_('file_path'), null=True, blank=True)
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(10)])
    type = models.CharField(_('type'), max_length=7, choices=FilmType.choices,
                            default=FilmType.MOVIE)

    class Meta:
        db_table = 'content\".\"film_work'
        ordering = ['created']
        verbose_name = _('Film')
        verbose_name_plural = _('Films')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE, verbose_name=_('Film'))
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name=_('Genre'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content\".\"genre_film_work'
        unique_together = ['film_work', 'genre']
        verbose_name = _('Film genre')
        verbose_name_plural = _('Films genres')

    def __str__(self):
        return self.genre.name


class PersonFilmwork(UUIDMixin):
    class RoleType(models.TextChoices):
        DIRECTOR = 'director', _('Director')
        ACTOR = 'actor', _('Actor')
        WRITER = 'writer', _('Writer')
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE, verbose_name=_('Film'))
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('full name'))
    role = models.CharField(_('Role'), max_length=8, choices=RoleType.choices,
                            default=RoleType.ACTOR)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content\".\"person_film_work'
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='film_work_person_role_idx')
        ]
        verbose_name = _('Film person')
        verbose_name_plural = _('Films persons')

    def __str__(self):
        return self.film_work.title
