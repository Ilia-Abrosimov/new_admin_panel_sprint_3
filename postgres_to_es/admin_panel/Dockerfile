FROM python:3.9
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app
COPY ./.env/ /app
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir
RUN apt-get update && apt-get install -y netcat
COPY . .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
