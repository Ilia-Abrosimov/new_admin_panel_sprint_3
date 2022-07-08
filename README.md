# Backend of administration part of online cinema.

Project consists of three sections:
1. [/postgres_to_es/admin_panel/](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/tree/main/postgres_to_es/admin_panel)

    Application to load movies through Django admin panel.

    * Database (Postgres) created by uses [.ddl](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/blob/main/postgres_to_es/postgres/create_database.ddl) file or [Django migrations](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/tree/main/postgres_to_es/admin_panel/movies).
    * For speed up the execution of database queries uses indexes.
    * Database filling by [script](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/tree/main/postgres_to_es/admin_panel/sql_to_postgres) for load data from sqlite to postgres.
    * Uuid is used as primary keys.
    * For validation of transfer data uses dataclasses.

2. [/postgres_to_es/admin_panel/movies/api/](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/tree/main/postgres_to_es/admin_panel/movies/api)
   
   Simple API for project, uses two method for receive all films or one film.
   
   Tests running by Postman and json [file](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/blob/main/postgres_to_es/admin_panel/movies/api/postman_tests.json).

3. [/postgres_to_es/etl/](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/tree/main/postgres_to_es/etl)

   The project uses ElasticSearch as a search engine.
   
   Set up an ETL process to transfer data from the database to elastic.
   * For validation data uses [pydantic](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/blob/main/postgres_to_es/etl/models.py).
   * For recovery connection with database or elastic made [backoff](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/blob/main/postgres_to_es/etl/tools.py) decorator.
   * Tests running by Postman and json [file](https://github.com/Ilia-Abrosimov/new_admin_panel_sprint_3/blob/main/postgres_to_es/etl/postman_tests.json).

Project start in 5 services in docker-compose: Database, Web(Admin Panel), Nginx, Elastic, ETL process.

For launch in development.

```bash
docker-compose -f docker-compose.dev.yml up -d
```

1. Create database schema

```bash
docker compose exec db psql -h 127.0.0.1 -U DB_USER -d DB_NAME -f create_database.ddl
```

2. Enter in web service

```bash
docker compose exec web bash
```

3. Load data from sqlite in postgresql

```bash
cd sql_to_postgres && python load_data.py
```

4. Start ETL proccess

```bash
docker compose exec etl python main.py
```
