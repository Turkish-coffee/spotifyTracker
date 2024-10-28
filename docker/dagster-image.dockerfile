# Dockerfile for dagster
FROM python:3.11.8-slim

WORKDIR /opt/dagster/dagster_home

RUN apt-get update && apt-get install -y \
    libpq-dev gcc


#manually installing psycopg2 cause it seems adding it in setup.py isnt enough
RUN pip install psycopg2 dagster dagster-webserver --find-links=https://github.com/dagster-io/build-grpcio/wiki/Wheels

# Copy the dbt project files into the container
COPY ../src/dagster /opt/dagster/dagster_home
COPY ../src/dbt /opt/dbt
COPY ../src/.env /opt/dagster/dagster_home

RUN pip install -e .[dev]
RUN . ./.env 

# Default command to run Dagster UI
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]