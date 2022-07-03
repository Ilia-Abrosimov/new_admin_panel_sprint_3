import logging

from elasticsearch import Elasticsearch, helpers

from models import ElasticFilmWork
from tools import backoff


class ElasticLoader:
    def __init__(self, es_host: str):
        self.es = Elasticsearch(es_host, verify_certs=False)

    @staticmethod
    @backoff()
    def send_data(es: Elasticsearch, es_data: list[ElasticFilmWork]) -> tuple[int, list]:
        query = [{'_index': 'movies', '_id': data.id, '_source': data.json()} for data in es_data]
        rows_count, errors = helpers.bulk(es, query)
        if errors:
            logging.error('Send data to elastic errors', extra={'query': query, 'errors': errors})
        return rows_count, errors
