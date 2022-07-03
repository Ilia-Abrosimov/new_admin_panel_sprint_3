import logging

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from tools import backoff

BATCH_SIZE = 1000


class PGSaver:

    def __init__(self, pg_conn: _connection, curs: DictCursor, offset: int):
        self.pg_conn = pg_conn
        self.curs = curs
        self.curs.execute("SET search_path TO content;")
        self.offset = offset

    @staticmethod
    @backoff()
    def get_data(query: str, curs: DictCursor) -> list:
        try:
            curs.execute(query)
            while data := curs.fetchmany(BATCH_SIZE):
                yield data
        except psycopg2.Error as error:
            logging.error(error)

    def get_ids(self, table: str, date: str) -> tuple:
        query = f'SELECT id from {table} ' \
                f"WHERE modified > '{date}' " \
                'ORDER BY modified '
        if table != 'genre':
            query += f'OFFSET {self.offset}'
        data = self.get_data(query, self.curs)
        ids = []
        for batch in data:
            for item in batch:
                ids.append(item[0])
        result = tuple(ids)
        return result

    def get_ids_for_persons(self, persons_ids: tuple[str]) -> tuple:
        query = 'SELECT fw.id FROM film_work fw ' \
                'LEFT JOIN person_film_work pfw ON pfw.film_work_id = fw.id ' \
                f'WHERE pfw.person_id IN {persons_ids} ' \
                'ORDER BY fw.modified'
        data = self.get_data(query, self.curs)
        ids = []
        for batch in data:
            for item in batch:
                ids.append(item[0])
        result = tuple(ids)
        return result

    def get_ids_for_genre(self, genres_ids: tuple) -> tuple:
        query = 'SELECT fw.id FROM film_work fw ' \
                'LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id ' \
                f'WHERE gfw.genre_id in {genres_ids} ' \
                'ORDER BY fw.modified ' \
                f'OFFSET {self.offset}'
        data = self.get_data(query, self.curs)
        ids = []
        for batch in data:
            for item in batch:
                ids.append(item[0])
        result = tuple(ids)
        return result

    def get_ids_for_filmwork(self, table_name: str, modified: str) -> tuple:
        objects_ids = self.get_ids(table_name, modified)
        if table_name == 'film_work':
            return objects_ids
        elif table_name == 'person':
            return self.get_ids_for_persons(objects_ids) if objects_ids else None
        elif table_name == 'genre':
            return self.get_ids_for_genre(objects_ids) if objects_ids else None

    def get_filmworks(self, filmwork_ids: tuple[str]) -> list:
        query = 'SELECT fw.id as fw_id, fw.title, fw.description, ' \
                'fw.rating, fw.type, fw.created, fw.modified, pfw.role, ' \
                'p.id as person_id, p.full_name, g.name as genre_name FROM film_work fw ' \
                'LEFT JOIN person_film_work pfw ON pfw.film_work_id = fw.id ' \
                'LEFT JOIN person p ON p.id = pfw.person_id ' \
                'LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id ' \
                'LEFT JOIN genre g ON g.id = gfw.genre_id ' \
                f'WHERE fw.id IN {filmwork_ids};'
        data = self.get_data(query, self.curs)
        res = []
        for batch in list(data):
            for row in batch:
                res.append(row)
        return res
