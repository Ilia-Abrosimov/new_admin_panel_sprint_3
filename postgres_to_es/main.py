import json
import logging
import time
from contextlib import closing
from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor

from es_loader import ElasticLoader
from models import FilmWork, PGSettings, ESSettings
from pg_extract import BATCH_SIZE, PGSaver
from state_control import state_init
from transform import parse_films_to_es_model


def elastic_load_data():
    dsl = PGSettings().dict()
    es_host = ESSettings().dict()
    state = state_init()
    es_saver = ElasticLoader(**es_host)
    if not es_saver.es.indices.exists(index="movies"):
        schema = open("elastic_schema.json", "r")
        data = json.loads(schema.read())
        es_saver.es.indices.create(index='movies', body=data)
    while True:
        try:
            with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn, pg_conn.cursor() as curs:
                date_from = state.get_state('date_from')
                offset = state.get_state('offset')
                postgres_loader = PGSaver(pg_conn, curs, offset)
                table_names = ['film_work', 'person', 'genre']
                for table_name in table_names:
                    while True:
                        filmwork_ids = postgres_loader.get_ids_for_filmwork(table_name, date_from)
                        if not filmwork_ids:
                            state.set_state('offset', 0)
                            break
                        filmwork_data = [
                            FilmWork.parse_obj(data)
                            for data in postgres_loader.get_filmworks(filmwork_ids)
                        ]
                        es_film_works = []
                        for film_id in filmwork_ids:
                            film_data = list(filter(lambda x: x.fw_id == film_id, filmwork_data))
                            es_film_works.append(parse_films_to_es_model(film_data, film_id))

                        response = es_saver.send_data(es_saver.es, es_film_works)
                        if response:
                            postgres_loader.offset += BATCH_SIZE
                            state.set_state('offset', postgres_loader.offset)

                    state.set_state('offset', 0)

                state.set_state('date_from', datetime.now().strftime('%Y-%m-%d'))

        except psycopg2.OperationalError:
            logging.error('Error connecting to Postgres database')
        time.sleep(1)


if __name__ == '__main__':
    elastic_load_data()
