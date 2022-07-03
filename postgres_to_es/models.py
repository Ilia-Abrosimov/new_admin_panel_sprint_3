from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class FilmWork(BaseModel):
    fw_id: str
    title: str
    description: Optional[str]
    rating: Optional[float]
    type: Optional[str]
    created: datetime
    modified: datetime
    role: Optional[str]
    person_id: Optional[str]
    full_name: Optional[str]
    genre_name: str


class ElasticFilmWork(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genre: list[str]
    title: str
    description: Optional[str]
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[Person]
    writers: list[Person]
