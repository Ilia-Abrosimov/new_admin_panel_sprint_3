import sqlite3
from contextlib import contextmanager
from dataclasses import astuple


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def prepare_data(data: list, model) -> list:
    prepared_data = []
    for row in data:
        obj = astuple(model(*row))
        prepared_data.append(obj)
    return prepared_data
