# Dockerfile for dbt
FROM python:3.11.8-slim

# Set the working directory
WORKDIR /app

# Install dbt (adjust the version to your needs)
RUN pip install dbt-core==1.8.7 dbt-postgres==1.8.2  python-dotenv

# Copy the dbt project files into the container
COPY ../src/dbt /app
COPY ../src/.env /app

ENV DBT_PROFILES_DIR=/app

CMD ["sh", "-c", "set -a && . /app/.env && dbt run --profile dbt"]