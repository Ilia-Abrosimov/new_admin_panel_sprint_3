import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from loaders import PostgresSaver, SQLiteLoader
from models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from tools import conn_context

load_dotenv()


def load_from_sqlite(connection: sqlite3.Connection, postge_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(postge_conn)
    sqlite_loader = SQLiteLoader()
    tables = {'film_work': FilmWork, 'genre': Genre, 'person': Person,
              'genre_film_work': GenreFilmWork, 'person_film_work': PersonFilmWork}
    for table, model in tables.items():
        for data in sqlite_loader.get_data(connection, table):
            postgres_saver.save_all_data(data, table, model)


if __name__ == '__main__':
    dsl = {'dbname': os.environ.get('DB_NAME'), 'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'), 'host': os.environ.get('DB_HOST', '127.0.0.1'),
           'port': os.environ.get('DB_PORT', 5432)}
    with conn_context('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
    pg_conn.close()
    sqlite_conn.close()
