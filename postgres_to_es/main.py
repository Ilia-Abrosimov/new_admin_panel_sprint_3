import json
import logging
import time
from contextlib import closing
from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor

from es_loader import ElasticLoader
from models import FilmWork
from pg_extract import BATCH_SIZE, PGSaver
from state_control import state_init
from transform import parse_films_to_es_model
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
ES_HOST = os.environ.get('ES_HOST')
ES_PORT = os.environ.get('ES_PORT')


def elastic_load_data():
    dsl = {'dbname': DB_NAME, 'user': DB_USER,
           'password': DB_PASSWORD, 'host': DB_HOST,
           'port': DB_PORT}
    es_host = f"http://{ES_HOST}:{ES_PORT}"
    state = state_init()
    while True:
        try:
            with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn, pg_conn.cursor() as curs:
                date_from = state.get_state('date_from')
                offset = state.get_state('offset')
                postgres_loader = PGSaver(pg_conn, curs, offset)
                es_saver = ElasticLoader(es_host=es_host)
                if not es_saver.es.indices.exists(index="movies"):
                    schema = open("elastic_schema.json", "r")
                    data = json.loads(schema.read())
                    es_saver.es.indices.create(index='movies', body=data)
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
                        postgres_loader.offset += BATCH_SIZE
                        state.set_state('offset', postgres_loader.offset)

                        es_film_works = []
                        for film_id in filmwork_ids:
                            film_data = list(filter(lambda x: x.fw_id == film_id, filmwork_data))
                            es_film_works.append(parse_films_to_es_model(film_data, film_id))

                        es_saver.send_data(es_saver.es, es_film_works)

                    state.set_state('offset', 0)

                state.set_state('date_from', datetime.now().strftime('%Y-%m-%d'))

        except psycopg2.OperationalError:
            logging.error('Error connecting to Postgres database')
        time.sleep(1)


if __name__ == '__main__':
    elastic_load_data()
