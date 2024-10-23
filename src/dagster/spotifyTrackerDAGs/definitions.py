
from dagster import Definitions, load_assets_from_modules
from .assets import spotify as spotify_assets
from .jobs.spotify_ELT_job_v1 import spotify_data_pipeline_job_v1
from.resources.db_conn import PgConnectionRessource
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../../.env')

all_assets = load_assets_from_modules([spotify_assets])

defs = Definitions(
    assets=all_assets,
    resources={"pg_res" : PgConnectionRessource(host=os.getenv("POSTGRES_HOST"),
                                                dbname=os.getenv("POSTGRES_DB"),
                                                port=os.getenv('POSTGRES_PORT'),
                                                user=os.getenv("POSTGRES_USER"),
                                                password=os.getenv("POSTGRES_PASSWORD")
                                                )},
    jobs=[spotify_data_pipeline_job_v1]
                
)
