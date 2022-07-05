from models import ElasticFilmWork, FilmWork


def parse_films_to_es_model(film_data: list[FilmWork], film_id: str) -> ElasticFilmWork:
    actors = {}
    writers = {}
    directors = {}
    genres = set()
    for row in film_data:
        genres.add(row.genre_name)
        if row.role == 'actor' and row.person_id not in actors:
            actors[row.person_id] = row.full_name
        elif row.role == 'writer' and row.person_id not in writers:
            writers[row.person_id] = row.full_name
        elif row.role == 'director' and row.person_id not in directors:
            directors[row.person_id] = row.full_name
    film = film_data[0]
    es_data = ElasticFilmWork(
        id=film_id, imdb_rating=film.rating, genre=list(genres), title=film.title,
        description=film.description, director=list(directors.values()),
        actors_names=list(actors.values()), writers_names=list(writers.values()),
        actors=[{'id': id, 'name': full_name} for id, full_name in actors.items()],
        writers=[{'id': id, 'name': full_name} for id, full_name in actors.items()],
    )
    return es_data
