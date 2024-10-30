from dagster import RunConfig, define_asset_job
from dagster_dbt import build_dbt_asset_selection, build_schedule_from_dbt_selection
from spotifyTrackerDAGs.assets.dbt_asssets import MyDbtConfig, dbt_analytics

my_dbt_job = define_asset_job(
    name="all_dbt_assets",
    selection=build_dbt_asset_selection(
        [dbt_analytics],
    ),
    config=RunConfig(
        ops={"dbt_analytics": MyDbtConfig(full_refresh=True, target='docker', seed=True)}
    ),
)

daily_dbt_assets_schedule = build_schedule_from_dbt_selection(
    [dbt_analytics],
    job_name="daily_dbt_models",
    cron_schedule="@daily",
    dbt_select="tag:daily",
    config=RunConfig(
        ops={"dbt_analytics": MyDbtConfig(full_refresh=True, target='docker', seed=True)}
    ),
)