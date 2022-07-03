# Заключительное задание первого модуля

Ваша задача в этом уроке — загрузить данные в Elasticsearch из PostgreSQL. Подробности задания в папке `etl`.

Для запуска сервис необходимо выполнить следующие действия:

1. Создать схему БД 


    `docker compose exec db psql -h 127.0.0.1 -U DB_USER -d DB_NAME -f create_database.ddl`

2. Перейти в контейнер web


    `docker compose exec web bash`

3. Загрузить данные из sqlite в postgresql


    `cd sql_to_postgres && python load_data.py`

4. Запустить перенос данных из postgresql в elasticsearch

    
    `cd .. && python main.py`
