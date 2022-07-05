FROM python:3.9
RUN mkdir /etl
WORKDIR /etl
COPY ../requirements.txt /etl
COPY ../.env/ /etl
RUN pip3 install --upgrade pip
RUN pip3 install -r /etl/requirements.txt --no-cache-dir
RUN apt-get update && apt-get install -y netcat
COPY . .
RUN chmod +x /etl/entrypoint.sh
ENTRYPOINT ["/etl/entrypoint.sh"]
