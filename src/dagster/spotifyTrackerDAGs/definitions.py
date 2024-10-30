from .assets.dbt_asssets import dbt_analytics, dbt_resource
from dagster import Definitions, load_assets_from_modules
from .assets import spotify_assets
from .jobs.spotify_jobs import spotify_data_pipeline_job, spotify_data_pipeline_job_schedule
from .jobs.dbt_jobs import my_dbt_job
from.resources.db_conn import PgConnectionRessource
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../../.env')

all_assets = load_assets_from_modules([spotify_assets])

defs = Definitions(
    assets=[*all_assets, dbt_analytics],
    resources={"pg_res" : PgConnectionRessource(host=os.getenv("POSTGRES_HOST"),
                                                dbname=os.getenv("POSTGRES_DB"),
                                                port=os.getenv('POSTGRES_PORT'),
                                                user=os.getenv("POSTGRES_USER"),
                                                password=os.getenv("POSTGRES_PASSWORD")
                                                ),
                "dbt" : dbt_resource
                },
    jobs=[spotify_data_pipeline_job, my_dbt_job],
    schedules=[spotify_data_pipeline_job_schedule]
)
