import logging
import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values
from tools import prepare_data


SIZE = 1000


class SQLiteLoader:
    @staticmethod
    def get_data(connection: sqlite3.Connection, table: str):
        curs = connection.cursor()
        query = f'SELECT * FROM {table};'
        try:
            curs.execute(query)
            while data := curs.fetchmany(SIZE):
                yield data
        except sqlite3.Error as error:
            logging.error(error)


class PostgresSaver:
    def __init__(self, conn: _connection):
        self.conn = conn

    def save_all_data(self, data_from_sqlite: list, table: str, model):
        data = prepare_data(data_from_sqlite, model)
        curs = self.conn.cursor()
        query = f'INSERT INTO content.{table} VALUES %s ON CONFLICT (id) DO NOTHING'
        try:
            execute_values(curs, query, data)
        except psycopg2.Error as error:
            logging.error(error)
